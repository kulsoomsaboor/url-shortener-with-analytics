from django.urls import path
from .views import LinkCreateView, analytics_view

urlpatterns = [
    path('create/', LinkCreateView.as_view(), name='link-create'),
    path('analytics/', analytics_view, name='analytics-view'),
]
