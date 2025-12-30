from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count, Avg
from .models import Expenses
from .serializers import ExpensesSerializer
from .filters import ExpenseFilter


class ExpensesPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_expenses(request):
    # Get user's expenses
    expenses = Expenses.objects.filter(user=request.user)
    
    # Apply filters
    expense_filter = ExpenseFilter(request.GET, queryset=expenses)
    filtered_expenses = expense_filter.qs
    
    # Check if any expenses exist
    if not filtered_expenses.exists():
        return Response({'message': 'No expenses found.'})
    
    # Add pagination
    paginator = ExpensesPagination()
    paginated_expenses = paginator.paginate_queryset(filtered_expenses, request)
    
    if paginated_expenses is not None:
        serializer = ExpensesSerializer(paginated_expenses, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    # Return all expenses if pagination fails
    serializer = ExpensesSerializer(filtered_expenses, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_expense(request):
    # Create new expense
    serializer = ExpensesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_expense(request, pk):
    # Find the expense
    try:
        expense = Expenses.objects.get(pk=pk, user=request.user)
    except Expenses.DoesNotExist:
        return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update the expense
    serializer = ExpensesSerializer(expense, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_expense(request, pk):
    # Find and delete the expense
    try:
        expense = Expenses.objects.get(pk=pk, user=request.user)
    except Expenses.DoesNotExist:
        return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    expense.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_summary(request):
    # Get user's expenses
    expenses = Expenses.objects.filter(user=request.user)
    
    # Apply filters
    expense_filter = ExpenseFilter(request.GET, queryset=expenses)
    filtered_expenses = expense_filter.qs
    
    # Calculate totals
    totals = filtered_expenses.aggregate(
        total_amount=Sum('amount'),
        total_count=Count('id'),
        average_amount=Avg('amount')
    )
    
    # Calculate category breakdown
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