import boto3
from django.db import models
from .utils import generate_short_code


dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')  
table = dynamodb.Table('ShortLinks')  

class Link(models.Model):
    original_url = models.URLField()
    short_code = models.CharField(max_length=8, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = generate_short_code()
        super().save(*args, **kwargs)

        try:
            table.put_item(Item={
                'short_code': self.short_code,
                'original_url': self.original_url
            })
        except Exception as e:
            print("Error syncing to DynamoDB:", e)

    def __str__(self):
        return f"{self.short_code} → {self.original_url}"
