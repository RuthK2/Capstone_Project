from rest_framework import serializers
from .models import Expenses


class ExpensesSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Expenses
        fields = ['id', 'user', 'amount', 'description', 'category', 'category_name', 'tags', 'date', 'timestamp']
        read_only_fields = ['id', 'user', 'category_name', 'timestamp']