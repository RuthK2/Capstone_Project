from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_expenses, name='list_expenses'),
    path('create/', views.create_expense, name='create_expense'),
    path('<int:pk>/update/', views.update_expense, name='update_expense'),
    path('<int:pk>/delete/', views.delete_expense, name='delete_expense'),
]