# Updating Lambda Function for Dynamic DynamoDB Lookup (Final Integration)

Fetch the original URL from **DynamoDB** dynamically using the `short_code` provided in the **API Gateway path** and redirect to it.


### Updated Lambda Function Code

```
import json
import boto3

# Initialize DynamoDB client (region must match your table’s region)
dynamodb = boto3.client('dynamodb', region_name='eu-north-1') 

def lambda_handler(event, context):
    # Get short_code from path parameters
    short_code = event.get("pathParameters", {}).get("short_code")

    if not short_code:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Short code is missing.'})
        }

    try:
        # Query DynamoDB for the short_code
        response = dynamodb.get_item(
            TableName='ShortLinks',  # Replace with your actual table name
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

### Testing

In Your Browser:
Visit your API Gateway URL:
Example:

[https://<random-id>.execute-api.<region>.amazonaws.com/](https://<random-id>.execute-api.<region>.amazonaws.com/)

Add the short code at the end:

[https://<random-id>.execute-api.<region>.amazonaws.com/t65N7A](https://<random-id>.execute-api.<region>.amazonaws.com/t65N7A)

Expected behavior: It should redirect you to the original URL stored for that short code.

In Lambda Console (Test Output):
If you trigger the Lambda function manually in the console using a test event, the output should look like:

```
{
  "statusCode": 302,
  "headers": {
    "Location": "https://www.codementor.io/blog/women-in-tech-6ev3m997u3"
  },
  "body": "{\"message\": \"Redirecting...\"}"
}
```

This confirms the full integration between API Gateway → Lambda → DynamoDB is working!




