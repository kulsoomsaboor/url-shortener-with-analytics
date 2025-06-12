from rest_framework import generics
from .models import Link
from .serializers import LinkSerializer

class LinkCreateView(generics.CreateAPIView):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
