### Updating Lambda Function for Analytics 

At this stage of development, we have two options:

1- Accessing DynamoDB in real time

2- Syncing DynamoDB data back to Django

Since our Django backend doesn’t yet sync real-time updates from DynamoDB, the Lambda-based solution (Option 1) offers a simpler and more direct path for logging analytics without delay.

### Goal:  Currently, Lambda is logging ip and user_agent on console, so we have to update it such that we save ip and user_agent for each short code aka logs history for each short_code.

Note: This function assumes that ClickLogs table is created manually in DynamoDB with id as "partition key".

The ClickLogs table stores:

id: unique log entry ID (UUID)

short_code: reference to the short link

timestamp: time of the click (UTC)

ip: client IP address

user_agent: browser/device info


### Update IAM Role Permissions

#### Step 1 : Find the IAM Role attached to your Lambda 
- Go to your Lambda function in AWS Console
- Click the "Configuration" tab. 
- On the left sidebar, click "Permissions". You’ll see a role like:

    Execution role: [urlRedirector-role-nyigfbcy](). Click on it, it opens the IAM console.

#### Step 2 : Add PutItem permission to the role
- In IAM, on the role page, Under "Permissions Policies"
- Click the inline policy you created last time for click_count logic. You can now modify the inline policy to include new permissions.

#### Step 3: Update custom policy for DynamoDB
- Click the JSON tab and paste :
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": ""arn:aws:dynamodb:<region>:<account-id>:table/ShortLinks"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem"
      ],
      "Resource": ""arn:aws:dynamodb:<region>:<account-id>:table/ClickLogs"

    }
  ]
}

```


### Updated Lambda Function:

```
import json
import boto3

import uuid
import datetime

dynamodb = boto3.client('dynamodb', region_name='eu-north-1')  

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
        print(f"Clicked: {short_code} | IP: {ip} | User-Agent: {user_agent}")
        
        # Save click log entry to separate table
        dynamodb.put_item(
            TableName='ClickLogs',
            Item={
                'id': {'S': str(uuid.uuid4())},
                'short_code': {'S': short_code},
                'timestamp': {'S': datetime.datetime.utcnow().isoformat()},
                'ip': {'S': ip},
                'user_agent': {'S': user_agent}
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


### Testing (on AWS Console)


```
{
  "pathParameters": {
    "short_code": "ABJD15"
  }
,
  "headers": {
    "X-Forwarded-For": "39.48.117.53",
    "User-Agent": "Mozilla/6.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.33 (KHTML, like Gecko) Chrome/138.0.1.0 Safari/577.36"
  }
}

```


### Response:

```
{
  "statusCode": 302,
  "headers": {
    "Location": "https://medium.com/must-know-computer-science"
  },
  "body": "{\"message\": \"Redirecting...\"}"
}

Function Logs:
START RequestId: d4cfdd9b-1567-4a82-a2e3-fed7d76d1bee Version: $LATEST
Clicked: ABJD15 | IP: 39.48.117.53 | User-Agent: Mozilla/6.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.33 (KHTML, like Gecko) Chrome/138.0.1.0 Safari/577.36
END RequestId: d4cfdd9b-1567-4a82-a2e3-fed7d76d1bee
REPORT RequestId: d4cfdd9b-1567-4a82-a2e3-fed7d76d1bee	Duration: 82.15 ms	Billed Duration: 83 ms	Memory Size: 128 MB	Max Memory Used: 86 MB

```

This confirms both the redirect works, and analytics were logged successfully.


### View Analytics:
 
After redirection, you can check the ClickLogs table in your DynamoDB tables having each shortcode's logs history beside it. (only the links that were clicked after incorporating the analytics logic will show the logs history.)
