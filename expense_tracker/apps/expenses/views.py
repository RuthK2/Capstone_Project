from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from .models import Expenses
from .serializers import ExpensesSerializer
from .filters import ExpenseFilter

class ExpensesPagination(PageNumberPagination):
    page_size = 5  # Number of expenses per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class ExpensesViewSet(viewsets.ModelViewSet):
    serializer_class = ExpensesSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExpenseFilter
    
    def get_queryset(self):
        return Expenses.objects.select_related('category', 'user').filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Function-based views for URLs (kept for backward compatibility)
@api_view(['GET'])
def list_expenses(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
    """
    List user's expenses with filtering and pagination.
    
    Query Parameters:
    - period: weekly, monthly, last_3_months
    - category: category ID
    - page: page number
    - page_size: items per page (max 100)
    """
    expenses = Expenses.objects.select_related('category', 'user').filter(user=request.user)
    
    # Apply filtering using the FilterSet
    expense_filter = ExpenseFilter(request.GET, queryset=expenses)
    filtered_expenses = expense_filter.qs
    
    # Check if expenses exist
    if not filtered_expenses.exists():
        return Response({'message': 'No expenses found.'})
    
    # Pagination
    paginator = ExpensesPagination()
    paginated_expenses = paginator.paginate_queryset(filtered_expenses, request)
    
    if paginated_expenses is not None:
        serializer = ExpensesSerializer(paginated_expenses, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    # Fallback if pagination fails
    serializer = ExpensesSerializer(filtered_expenses, many=True)
    return Response(serializer.data)




@api_view(['POST'])
def create_expense(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
    """
    Create a new expense for the authenticated user.
    
    Required fields:
    - amount: decimal
    - description: string
    - category: category ID
    """
    serializer = ExpensesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_expense(request, pk):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        expense = Expenses.objects.select_related('category', 'user').get(pk=pk, user=request.user)
    except Expenses.DoesNotExist:
        return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ExpensesSerializer(expense, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_expense(request, pk):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        expense = Expenses.objects.select_related('category', 'user').get(pk=pk, user=request.user)
    except Expenses.DoesNotExist:
        return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    expense.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def expense_summary(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
    """
    Get expense analytics and summary for the authenticated user.
    
    Query Parameters:
    - period: weekly, monthly, last_3_months (optional)
    - category: category ID (optional)
    
    Returns:
    - Total amount, count, average
    - Category breakdown with percentages
    """
    expenses = Expenses.objects.select_related('category', 'user').filter(user=request.user)
    
    # period filtering using the same FilterSet
    expense_filter = ExpenseFilter(request.GET, queryset=expenses)
    filtered_expenses = expense_filter.qs
    
    # Basic totals
    totals = filtered_expenses.aggregate(
        total_amount=Sum('amount'),
        total_count=Count('id'),
        average_amount=Avg('amount')
    )
    
    # Category breakdown with percentages
    categories = filtered_expenses.values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    total_amount = totals['total_amount'] or 0
    category_breakdown = []
    for cat in categories:
        percentage = (cat['total'] / total_amount * 100) if total_amount > 0 else 0
        category_breakdown.append({
            'name': cat['category__name'],
            'total': cat['total'],
            'count': cat['count'],
            'percentage': round(percentage, 2)
        })
    
    return Response({
        'summary': {
            'total_amount': total_amount,
            'total_count': totals['total_count'] or 0,
            'average_amount': round(totals['average_amount'] or 0, 2)
        },
        'category_breakdown': category_breakdown,
        'period': request.GET.get('period', 'all_time')
    })
