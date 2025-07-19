import random
import string

import boto3

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
short_links_table = dynamodb.Table('ShortLinks')
click_log_table = dynamodb.Table('ClickLogs')


def sync_to_dynamodb(short_code, original_url):
    try:
        short_links_table.put_item(Item={
            'short_code': short_code,
            'original_url': original_url
        })
    except Exception as e:
        print("Error syncing to DynamoDB:", e)

