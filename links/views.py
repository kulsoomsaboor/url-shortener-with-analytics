from rest_framework import generics, status
from rest_framework.response import Response
from .models import Link
from .serializers import LinkSerializer
from .utils import generate_short_code

import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')  
table = dynamodb.Table('ShortLinks')  


class LinkCreateView(generics.CreateAPIView):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer

    def create(self, request, *args, **kwargs):
        original_url = request.data.get('original_url')

        # Check if the original URL already exists
        existing = Link.objects.filter(original_url=original_url).first()
        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Generate a unique short code
        short_code = generate_short_code()
        while Link.objects.filter(short_code=short_code).exists():
            short_code = generate_short_code()

        # Create and save the new link
        new_link = Link.objects.create(original_url=original_url, short_code=short_code)
        serializer = self.get_serializer(new_link)

        # Save to DynamoDB
        try:
            table.put_item(Item={
                'short_code': short_code,
                'original_url': original_url
            })
        except Exception as e:
            print("Error syncing to DynamoDB:", e)


        return Response(serializer.data, status=status.HTTP_201_CREATED)




    