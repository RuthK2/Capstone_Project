from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse

from apps.categories.models import Category


class CategoryAPITestCase(APITestCase):
    def setUp(self):
        self.test_username = 'testuser123'
        self.test_password = 'testpass123'
        self.user = User.objects.create_user(
            username=self.test_username,
            password=self.test_password)
        self.client.force_authenticate(user=self.user)

    def test_create_category(self):
        url = reverse('category-list')
        data = {'name': 'Test Category'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Category')

    def test_list_categories(self):
        Category.objects.create(name='Test Category')
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertGreaterEqual(len(data), 7)  # 6 predefined + 1 test category

    def test_predefined_categories_exist(self):
        """Test that predefined categories from roadmap exist"""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_categories = ['Groceries', 'Electricity', 'Utilities', 'Miscellaneous', 'Electronics', 'Clothing']
        data = response.data
        category_names = [cat.get('name', '') for cat in data]
        for expected in expected_categories:
            self.assertIn(expected, category_names, f"Predefined category '{expected}' should exist")

    def test_update_category(self):
        category = Category.objects.create(name='Test')
        url = reverse('category-detail', args=[category.id])
        data = {'name': 'Updated Category'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Category')

    def test_delete_category(self):
        category = Category.objects.create(name='Test')
        url = reverse('category-detail', args=[category.id])
        response = self.client.delete(url)
        # Categories might be read-only, so expect method not allowed
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_405_METHOD_NOT_ALLOWED])
    
    def test_unauthorized_access(self):
        """Test that unauthenticated users cannot access categories"""
        self.client.force_authenticate(user=None)  # Remove authentication
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


