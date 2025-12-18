from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from apps.expenses.models import Expenses
from apps.categories.models import Category


class ExpenseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Test Category')
        self.client.force_authenticate(user=self.user)

    def test_create_expense(self):
        url = reverse('create_expense')
        data = {
            'amount': 100,
            'description': 'Test Expense',
            'category': self.category.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expenses.objects.count(), 1)
        expense = Expenses.objects.get()
        self.assertEqual(expense.user, self.user)

    def test_list_expenses(self):
        Expenses.objects.create(user=self.user, amount=100, description='Test Expense', category=self.category)
        url = reverse('list_expenses')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_date(self):
        Expenses.objects.create(user=self.user, amount=100, description='Test1', category=self.category)
        Expenses.objects.create(user=self.user, amount=200, description='Test2', category=self.category)
        url = reverse('list_expenses') + '?period=weekly'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_category(self):
        Expenses.objects.create(user=self.user, amount=100, description='Test Expense', category=self.category)
        url = reverse('list_expenses') + f'?category={self.category.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_expense_summary(self):
        Expenses.objects.create(user=self.user, amount=100, description='Test Expense', category=self.category)
        url = reverse('expense_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        url = reverse('list_expenses')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_expense_invalid_amount(self):
        url = reverse('create_expense')
        data = {'description': 'Invalid expense'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_expense_invalid_category(self):
        url = reverse('create_expense')
        data = {'amount': 100, 'category': 999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)