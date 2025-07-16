## Updating Lambda Function for Tracking Click Count of Links

Add click count tracking logic to the Lambda function. Then, update its IAM permissions to allow it to perform UpdateItem operations in DynamoDB. Finally, test the updated behavior.


### 1. Update Lambda Function
```

import json
import boto3

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
Note: Even if click_count was not previously set for a short code, DynamoDB will initialize it to 1 the first time a user clicks the link. This is thanks to the ADD operation which treats missing values as zero.

### 2. Give Permissions
 
#### Step 1 : Find the IAM Role attached to your Lambda 
- Go to your Lambda function in AWS Console
- Click the "Configuration" tab. 
- On the left sidebar, click "Permissions". You’ll see a role like:

    Execution role: [urlRedirector-role-nyigfbcy](). Click on it, it opens the IAM console.

#### Step 2 : Add UpdateItem permission to the role
- In IAM, on the role page, click "Add permissions"
- Click "Create inline policy"

#### Step 3: Define a custom policy for DynamoDB
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
      "Resource": "arn:aws:dynamodb:eu-north-1:<your-account-id>:table/ShortLinks"

    }
  ]
}
```
- Then, click Next → Next → Create policy

### 3. Testing

####  Redirection:
- Using the AWS console to run test events. Create a new test event and paste this code :

```
{
  "pathParameters": {
    "short_code": "abc123"
  },
  "headers": {
    "X-Forwarded-For": "39.48.112.53",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
  }
}

```

 You should now see a 302 status (if the short code exists).

- Using a real API Gateway endpoint in our browser :

Enter your Full Url with the short_code in the browser as:

[https://<random-id>.execute-api.<region>.amazonaws.com/dev/t65N7J]()


### Increase in click count:
 
After redirection using any of the above methods, you can check the updated click_count in your DynamoDB table under the corresponding item.

### Show Logs in CloudWatch on AWS:

To see the logs we can go to CloudWatch and see the latest log stream. We should something like: 

##### START RequestId: ...
##### Clicked: t65N7A | IP: 39.48.112.53 | User-Agent: Mozilla/5.0 ...
##### END RequestId: ...






