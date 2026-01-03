from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import logging
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from .models import UserProfile

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        UserProfile.objects.get_or_create(user=user)
        return Response({
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    # Login user and return JWT tokens
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout(request):
    # Simple logout (JWT tokens are stateless)
    return Response({'message': 'Logout successful'})


@api_view(['GET'])
def protected_view(request):
    # Check if user is logged in
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'message': 'This is a protected endpoint'})


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def budget(request):
    # Get or update user's monthly budget
    try:
        # Ensure UserProfile exists
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            return Response({'monthly_budget': profile.monthly_budget})
        
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Budget updated successfully', 'monthly_budget': serializer.data['monthly_budget']})
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Budget error: {str(e)}")
        return Response({'error': 'Budget operation failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)