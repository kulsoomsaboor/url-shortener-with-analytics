
## Giving Lambda Permission to Read from DynamoDB (Access Control + Basic Integration)

## Step: Enable Lambda to Look Up Short Codes in DynamoDB

To allow Lambda to read from DynamoDB (i.e., perform lookups like `t65N7A → original_url`), follow these steps:

### 1. Go to the Lambda Console
- Open your function in the **AWS Lambda Console**.

### 2. Locate the Execution Role
- In the **Configuration tab**, scroll down to **Permissions**.
- Click on the linked **IAM role name** (under Execution Role).

### 3. Attach a DynamoDB Read-Only Policy
- In the IAM Role console:
  - Click **Add permissions** → **Attach policies**.
  - Search for: `AmazonDynamoDBReadOnlyAccess`
  - Select and **attach** this policy.

 This gives your Lambda function read access to all DynamoDB tables (sufficient for basic prototyping and testing).

---

## Step: Update Lambda Function Code to Fetch from DynamoDB

We will now implement the actual database lookup in the Lambda function.

This version still uses a **hardcoded short_code value** for basic testing.

### Lambda Function Code (Basic Read from DynamoDB)

```
import json
import boto3

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    try:
        response = dynamodb.get_item(
            TableName='ShortLinks',  
            Key={
                'short_code': {'S': 't65N7A'}  # Hardcoded short_code for testing
            }
        )
        item = response.get('Item', None)

        if item:
            return {
                'statusCode': 200,
                'body': json.dumps({'original_url': item['original_url']['S']})
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Short code not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

```

### Testing (Basic Hardcoded Example)
Run a test in the Lambda console.

Expected Output:
```
{
  "statusCode": 200,
  "body": "{\"original_url\": \"https://www.codementor.io/blog/women-in-tech-6ev3m997u3\"}"
}

```
This confirms that Lambda can now access and read data from your DynamoDB table.

Next Step:
Replace the hardcoded short_code with a dynamic value from the API Gateway path parameter.
Example:
short_code = event['pathParameters']['short_code']


