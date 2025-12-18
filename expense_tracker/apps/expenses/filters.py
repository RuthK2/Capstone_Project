import django_filters
from django.utils import timezone
from datetime import timedelta
from .models import Expenses


class ExpenseFilter(django_filters.FilterSet):
    # Date period filtering
    period = django_filters.ChoiceFilter(
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('last_3_months', 'Last 3 Months'),
        ],
        method='filter_by_period'
    )
    
    # Category filtering
    category = django_filters.NumberFilter(field_name='category__id')
    
    # Date range filtering
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    
    class Meta:
        model = Expenses
        fields = ['category', 'period', 'date_from', 'date_to']
    
    def filter_by_period(self, queryset, name, value):
        if value == 'weekly':
            start_date = timezone.now().date() - timedelta(days=7)
        elif value == 'monthly':
            start_date = timezone.now().date() - timedelta(days=30)
        elif value == 'last_3_months':
            start_date = timezone.now().date() - timedelta(days=90)
        else:
            return queryset
        
        return queryset.filter(date__gte=start_date)