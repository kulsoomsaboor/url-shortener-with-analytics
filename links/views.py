from rest_framework import generics, status
from rest_framework.response import Response
from .models import Link
from .serializers import LinkSerializer
from .utils import generate_short_code, sync_to_dynamodb, short_links_table, click_log_table
from django.shortcuts import render



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

        sync_to_dynamodb(short_code, original_url)


        return Response(serializer.data, status=status.HTTP_201_CREATED)

def analytics_view(request):
    try:
        response_short_links = short_links_table.scan()
        items_short_links = response_short_links.get('Items', [])
    except Exception as e:
        items_short_links = []
        print("Error fetching from DynamoDB (short_links):", e)
    
    try:
        response_click_logs = click_log_table.scan()
        items_click_logs = response_click_logs.get('Items', [])
    except Exception as e:
        items_click_logs = []
        print("Error fetching from DynamoDB (click_logs):", e)

    # Group click logs by short_code
    logs_by_code = {}
    for log in items_click_logs:
        code = log.get('short_code')
        logs_by_code.setdefault(code, []).append(log)

    print("Click Logs Fetched:")
    
    for log in items_click_logs:
        print(log)


    return render(request, 'links/analytics.html', {
        'items_short_links': items_short_links,
        'logs_by_code': logs_by_code
    })