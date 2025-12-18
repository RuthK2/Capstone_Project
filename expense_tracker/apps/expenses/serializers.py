from rest_framework import serializers
from .models import Expenses
from apps.categories.models import Category


class ExpensesSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Expenses
        fields = ['id', 'user', 'amount', 'description', 'category', 'category_name', 'date', 'timestamp']
        read_only_fields = ['id', 'user', 'category_name', 'timestamp']
    
    def validate_category(self, value):
        """Validate that category exists"""
        try:
            Category.objects.get(id=value.id if hasattr(value, 'id') else value)
            return value
        except Category.DoesNotExist:
            raise serializers.ValidationError("Invalid category ID")
    
    def create(self, validated_data):
        # User is set in the view
        return super().create(validated_data)