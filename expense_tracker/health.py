from django.http import JsonResponse
from django.contrib.auth.models import User
from apps.categories.models import Category
from apps.authentication.models import UserProfile

def health_check(request):
    """Simple endpoint to check database status"""
    try:
        user_count = User.objects.count()
        category_count = Category.objects.count()
        profile_count = UserProfile.objects.count()
        
        return JsonResponse({
            'status': 'ok',
            'database': 'connected',
            'users': user_count,
            'categories': category_count,
            'profiles': profile_count
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        })