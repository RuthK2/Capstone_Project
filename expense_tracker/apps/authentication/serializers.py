from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from django.db import IntegrityError


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField() 
    password = serializers.CharField()
    password2 = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists")
            
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')  # Remove password2 before creating user
        try:
            return User.objects.create_user(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError("Username already exists")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['monthly_budget']
