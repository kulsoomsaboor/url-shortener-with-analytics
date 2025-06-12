from django.urls import path
from .views import LinkCreateView

urlpatterns = [
    path('create/', LinkCreateView.as_view(), name='link-create'),
]
