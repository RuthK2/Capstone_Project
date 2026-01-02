from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer, UserProfileSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    # Create new user account
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create JWT tokens for the new user
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    # Login user and return JWT tokens
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        # Ensure UserProfile exists
        from .models import UserProfile
        UserProfile.objects.get_or_create(user=user)
        
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
    from .models import UserProfile
    
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