from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Expenses
from .serializers import ExpensesSerializer

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
    if not expenses.exists():
        return Response({'message': 'No expenses yet. Start tracking your expenses!'})
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
