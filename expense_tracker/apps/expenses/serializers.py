from rest_framework import serializers
from .models import Expenses
from apps.categories.models import Category


class ExpensesSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField()
    category = serializers.IntegerField(write_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    date = serializers.DateField(read_only=True)

    def create(self, validated_data):
        category_id = validated_data.pop('category')
        category = Category.objects.get(id=category_id)
        expense = Expenses.objects.create(
            category=category,
            **validated_data
        )
        return expense

    def update(self, instance, validated_data):
        if 'category' in validated_data:
            category_id = validated_data.pop('category')
            instance.category = Category.objects.get(id=category_id)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance