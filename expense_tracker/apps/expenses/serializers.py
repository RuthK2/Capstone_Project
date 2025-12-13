from rest_framework import serializers
from .models import Expenses


class ExpensesSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField()
    category = serializers.CharField(source='category.name', read_only=True)
    date = serializers.DateField(read_only=True)

    def create(self, validated_data):
        return Expenses.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.amount = validated_data.get('amount', instance.amount)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance