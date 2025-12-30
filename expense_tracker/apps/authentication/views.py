from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer, UserSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def user_stats(request):
    # Get user statistics
    from django.contrib.auth.models import User
    
    total_users = User.objects.count()
    admin_users = User.objects.filter(is_superuser=True).count()
    regular_users = total_users - admin_users
    
    # Get recent users (last 5)
    recent_users = User.objects.order_by('-date_joined')[:5].values('username', 'email', 'date_joined', 'is_superuser')
    
    return Response({
        'total_users': total_users,
        'admin_users': admin_users,
        'regular_users': regular_users,
        'recent_users': list(recent_users)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def create_admin(request):
    # Create admin user using registration logic
    try:
        # Check if admin already exists
        if User.objects.filter(username='admin').exists():
            return Response({'message': 'Admin user already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create regular user first
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # Make them superuser
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        return Response({
            'message': 'Admin created successfully',
            'username': 'admin',
            'password': 'admin123',
            'admin_url': 'https://web-production-c227c.up.railway.app/admin/'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
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