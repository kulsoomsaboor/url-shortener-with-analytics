### Integrating Geo-IP Tracking into Lambda Function for Click Logging

### ### Goal: Track the user's geographical location (country and region) for each click event using a Geo-IP API.
 

### ClickLogs Table Now Stores:

- `id`: Unique log entry ID (UUID)
- `short_code`: Reference to the short link
- `timestamp`: Time of the click (UTC)
- `ip`: Client IP address
- `user_agent`: Browser/device info
- `country`: Client’s country (via IP lookup)
- `region`: Client’s region (via IP lookup)
          

**Note**: No IAM permission updates required if the Lambda role already has `PutItem` access for the `ClickLogs` table.


### Updated Lambda Function:

```
import json
import boto3

import uuid
import datetime

import urllib.request


dynamodb = boto3.client('dynamodb', region_name='eu-north-1')  

def get_location_from_ip(ip_address):
    try:
        with urllib.request.urlopen(f'https://ipapi.co/{ip_address}/json/') as response:
            data = json.load(response)
            return {
                'country': data.get('country_name', 'Unknown'),
                'region': data.get('region', 'Unknown'),
            }
    except Exception as e:
        print(f"Error fetching location: {e}")
        return {
            'country': 'Unknown',
            'region': 'Unknown',
        }


def lambda_handler(event, context):
    short_code = event.get("pathParameters", {}).get("short_code")

    if not short_code:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Short code is missing.'})
        }

    try:
        response = dynamodb.get_item(
            TableName='ShortLinks',
            Key={
                'short_code': {'S': short_code}
            }
        )

        item = response.get('Item')
        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Short code not found.'})
            }

        original_url = item['original_url']['S']

        dynamodb.update_item(
            TableName='ShortLinks',
            Key={'short_code': {'S': short_code}},
            UpdateExpression="ADD click_count :inc",
            ExpressionAttributeValues={':inc': {'N': '1'}}
        )

        ip = event['headers'].get('X-Forwarded-For', 'Unknown')
        user_agent = event['headers'].get('User-Agent', 'Unknown')
        
        # Get location from IP
        location = get_location_from_ip(ip)

        # Log click to ClickLogs table
        dynamodb.put_item(
            TableName='ClickLogs',
            Item={
                'id': {'S': str(uuid.uuid4())},
                'short_code': {'S': short_code},
                'timestamp': {'S': datetime.datetime.utcnow().isoformat()},
                'ip': {'S': ip},
                'user_agent': {'S': user_agent},
                'country': {'S': location['country']},
                'region': {'S': location['region']},
            }
        )
        
        return {
            'statusCode': 302,
            'headers': {
                'Location': original_url
            },
            'body': json.dumps({'message': 'Redirecting...'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

```

### Testing:
```
{
  "pathParameters": {
    "short_code": "BsDTOh"
  },
  "headers": {
    "X-Forwarded-For": "39.48.117.53",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.33 (KHTML, like Gecko) Chrome/138.0.1.0 Safari/577.36"
  }
}

```

You should now see a 302 status (if the short code exists).


### Viewing Location Info:

After redirection, you can verify the `country` and `region` fields in the `ClickLogs` table for the corresponding `short_code`. Each click entry should now contain geographical information derived from the IP address.
