from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count, Avg
from .models import Expenses
from .serializers import ExpensesSerializer

class ExpensesPagination(PageNumberPagination):
    page_size = 5  # Number of expenses per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class ExpensesViewSet(viewsets.ModelViewSet):
    queryset = Expenses.objects.all()
    serializer_class = ExpensesSerializer

    def create_expense(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update_expense(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete_expense(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Function-based views for URLs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_expenses(request):
    expenses = Expenses.objects.filter(user=request.user)
    
    # date filtering
    period = request.GET.get('period')
    if period == 'weekly':
        expenses = expenses.filter(date__gte='2025-01-01')  # Last 7 days
    elif period == 'monthly':
        expenses = expenses.filter(date__gte='2024-12-01')  # Last 30 days
    elif period == 'last_3_months':
        expenses = expenses.filter(date__gte='2024-10-01')  # Last 90 days
    
    # category filtering
    category = request.GET.get('category')
    if category:
        try:
            expenses = expenses.filter(category=category)
        except Exception:
            return Response({'error': 'Invalid category ID'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if expenses exist first
    if not expenses.exists():
        return Response({'message': 'No expenses found.'})
    
    # Pagination
    paginator = ExpensesPagination()
    paginated_expenses = paginator.paginate_queryset(expenses, request)
    
    if paginated_expenses is not None:
        serializer = ExpensesSerializer(paginated_expenses, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    # Fallback if pagination fails
    serializer = ExpensesSerializer(expenses, many=True)
    return Response(serializer.data)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_expense(request):
    serializer = ExpensesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_expense(request, pk):
    try:
        expense = Expenses.objects.get(pk=pk, user=request.user)
    except Expenses.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = ExpensesSerializer(expense, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_expense(request, pk):
    try:
        expense = Expenses.objects.get(pk=pk, user=request.user)
    except Expenses.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    expense.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_summary(request):
    expenses = Expenses.objects.filter(user=request.user)
    
    totals = expenses.aggregate(
    total_amount=Sum('amount'),
    total_count=Count('id'),
    average_amount=Avg('amount')
    )
    
    categories = expenses.values('category__name').annotate(total=Sum('amount'))
    
    return Response({
        'total_amount': totals['total_amount'] or 0,
        'total_count': totals['total_count'] or 0,
        'average_amount': totals['average_amount'] or 0,
        'categories': list(categories)
    })
