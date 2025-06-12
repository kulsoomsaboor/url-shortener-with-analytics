
from rest_framework import serializers
from .models import Link

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ['id', 'original_url', 'short_code', 'created_at']
        read_only_fields = ['short_code', 'created_at']
