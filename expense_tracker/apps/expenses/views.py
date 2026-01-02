import logging
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from .filters import ExpenseFilter
from .models import Expenses
from .serializers import ExpensesSerializer

logger = logging.getLogger(__name__)

# Configurable constants
MAX_STREAK_DAYS = getattr(settings, 'EXPENSE_MAX_STREAK_DAYS', 30)
MAX_PAGE_SIZE = getattr(settings, 'EXPENSE_MAX_PAGE_SIZE', 100)


class ExpenseRateThrottle(UserRateThrottle):
    scope = 'expense'


class SummaryRateThrottle(UserRateThrottle):
    scope = 'summary'


def validate_query_params(request):
    """Validate common query parameters"""
    errors = []
    
    # Validate page_size
    page_size = request.GET.get('page_size')
    if page_size:
        try:
            page_size_int = int(page_size)
            if page_size_int < 1 or page_size_int > MAX_PAGE_SIZE:
                errors.append(f'page_size must be between 1 and {MAX_PAGE_SIZE}')
        except ValueError:
            errors.append('page_size must be a valid integer')
    
    # Validate period
    valid_periods = ['weekly', 'monthly', 'last_3_months', 'yearly']
    period = request.GET.get('period')
    if period and period not in valid_periods:
        errors.append(f'period must be one of: {", ".join(valid_periods)}')
    
    return errors


class ExpensesPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_expenses(request):
    # Validate query parameters
    validation_errors = validate_query_params(request)
    if validation_errors:
        return Response({'error': validation_errors}, status=status.HTTP_400_BAD_REQUEST)
    
    expenses = Expenses.objects.filter(user=request.user).select_related('category').order_by('-date')
    expense_filter = ExpenseFilter(request.GET, queryset=expenses)
    filtered_expenses = expense_filter.qs
    
    if not filtered_expenses.exists():
        return Response({'error': 'No expenses found.'}, status=status.HTTP_404_NOT_FOUND)
    
    paginator = ExpensesPagination()
    paginated_expenses = paginator.paginate_queryset(filtered_expenses, request)
    
    if paginated_expenses is not None:
        serializer = ExpensesSerializer(paginated_expenses, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = ExpensesSerializer(filtered_expenses, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([ExpenseRateThrottle])
def create_expense(request):
    serializer = ExpensesSerializer(data=request.data)
    if serializer.is_valid():
        expense = serializer.save(user=request.user)
        # Clear user's summary cache when new expense is created
        cache_pattern = f"summary_{request.user.id}_*"
        cache.delete_many([key for key in cache._cache.keys() if key.startswith(f"summary_{request.user.id}_")])
        logger.info(f"Created expense {expense.id} for user {request.user.id}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@throttle_classes([ExpenseRateThrottle])
def update_expense(request, pk):
    try:
        expense = Expenses.objects.select_related('category').get(pk=pk, user=request.user)
    except Expenses.DoesNotExist:
        return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ExpensesSerializer(expense, data=request.data)
    if serializer.is_valid():
        serializer.save()
        # Clear user's summary cache when expense is updated
        cache.delete_many([key for key in cache._cache.keys() if key.startswith(f"summary_{request.user.id}_")])
        logger.info(f"Updated expense {pk} for user {request.user.id}")
        return Response(serializer.data)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([ExpenseRateThrottle])
def delete_expense(request, pk):
    try:
        expense = Expenses.objects.get(pk=pk, user=request.user)
    except Expenses.DoesNotExist:
        return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    expense.delete()
    # Clear user's summary cache when expense is deleted
    cache.delete_many([key for key in cache._cache.keys() if key.startswith(f"summary_{request.user.id}_")])
    logger.info(f"Deleted expense {pk} for user {request.user.id}")
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SummaryRateThrottle])
def summary(request):
    # Validate query parameters
    validation_errors = validate_query_params(request)
    if validation_errors:
        return Response({'error': validation_errors}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create cache key based on user and filters
    cache_key = f"summary_{request.user.id}_{hash(str(sorted(request.GET.items())))}"
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for summary user {request.user.id}")
        return Response(cached_result)
    
    expenses = Expenses.objects.filter(user=request.user).select_related('category')
    expense_filter = ExpenseFilter(request.GET, queryset=expenses)
    filtered_expenses = expense_filter.qs
    
    # Optimize: Single query for all aggregations
    current_month = timezone.now().date().replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    
    # Combined aggregation query
    summary_data = filtered_expenses.aggregate(
        total_amount=Sum('amount'),
        total_count=Count('id'),
        average_amount=Avg('amount'),
        current_month_total=Sum('amount', filter=Q(date__gte=current_month)),
        last_month_total=Sum('amount', filter=Q(date__gte=last_month, date__lt=current_month))
    )
    
    categories = filtered_expenses.values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    total_amount = summary_data['total_amount'] or 0
    current_month_total = summary_data['current_month_total'] or 0
    last_month_total = summary_data['last_month_total'] or 0
    
    category_breakdown = []
    for cat in categories:
        percentage = (cat['total'] / total_amount * 100) if total_amount > 0 else 0
        category_breakdown.append({
            'name': cat['category__name'],
            'total': cat['total'],
            'count': cat['count'],
            'percentage': round(percentage, 2)
        })
    
    # Get monthly budget safely
    monthly_budget = 0
    try:
        if hasattr(request.user, 'userprofile') and request.user.userprofile:
            monthly_budget = request.user.userprofile.monthly_budget or 0
    except Exception as e:
        logger.warning(f"Error accessing user budget for user {request.user.id}: {e}")
        monthly_budget = 0
    
    budget_status = {
        'monthly_budget': monthly_budget,
        'spent': total_amount,
        'remaining': monthly_budget - total_amount,
        'percentage_used': round((total_amount / monthly_budget * 100), 2) if monthly_budget > 0 else 0
    }
    
    # Calculate month-over-month change
    if last_month_total > 0:
        month_change = ((current_month_total - last_month_total) / last_month_total) * 100
    else:
        month_change = 100 if current_month_total > 0 else 0
    
    # Get top category for current month (optimized)
    top_category = filtered_expenses.filter(date__gte=current_month).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total').first()
    
    spending_insights = {
        'current_month_spending': current_month_total,
        'last_month_spending': last_month_total,
        'month_over_month_change': round(month_change, 2),
        'trend': 'increasing' if month_change > 0 else 'decreasing' if month_change < 0 else 'stable',
        'top_category_this_month': top_category['category__name'] if top_category else None,
        'top_category_amount': top_category['total'] if top_category else 0
    }
    
    result = {
        'summary': {
            'total_amount': total_amount,
            'total_count': summary_data['total_count'] or 0,
            'average_amount': round(summary_data['average_amount'] or 0, 2)
        },
        'category_breakdown': category_breakdown,
        'budget_status': budget_status,
        'spending_insights': spending_insights,
        'period': request.GET.get('period', 'all_time')
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, result, 300)
    logger.info(f"Cached summary for user {request.user.id}")
    
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def insights(request):
    try:
        expenses = Expenses.objects.filter(user=request.user)
        last_7_days = timezone.now().date() - timedelta(days=7)
        weekly_expenses = expenses.filter(date__gte=last_7_days)
        weekly_total = weekly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        daily_average = weekly_total / 7
        
        spending_days = set(weekly_expenses.values_list('date', flat=True))
        streak = 0
        current_date = timezone.now().date()
        
        while current_date in spending_days and streak < MAX_STREAK_DAYS:
            streak += 1
            current_date -= timedelta(days=1)
        
        warnings = []
        # Dynamic threshold based on user's average
        user_avg = expenses.aggregate(Avg('amount'))['amount__avg'] or 0
        if weekly_total > user_avg * 7 * 1.5:  # 50% above weekly average
            warnings.append("High spending this week")
        
        return Response({
            'weekly_spending': float(weekly_total),
            'daily_average': round(daily_average, 2),
            'spending_streak_days': streak,
            'warnings': warnings,
            'insights': [
                f"You've spent money {streak} days in a row" if streak > 1 else "No recent spending streak",
                f"Your daily average this week is ${daily_average:.2f}",
                f"Weekly spending: ${weekly_total}"
            ]
        })
    except Exception as e:
        logger.error(f"Error generating insights for user {request.user.id}: {e}")
        return Response({
            'error': 'Unable to generate insights at this time'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)