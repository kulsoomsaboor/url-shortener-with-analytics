## Accessing Services via AWS Console

Go to: **AWS Console**  
  → **Dashboard**  
  → **Services**  
  → Select **Lambda** / **API Gateway**

---

## Overview

We define a Lambda function and connect it to an API Gateway to trigger redirection logic based on dynamic URLs.

### Key Points:

- After each code update in Lambda, you **must deploy** the changes.
- A **Lambda function is triggered by events**.
- In this case, the event source is **API Gateway – HTTP**.
- This means any incoming HTTP request that matches the configuration in API Gateway will trigger our Lambda function.
- We must **connect a specific API Gateway** as a trigger to our Lambda function manually.

---

## Lambda Function Code

```
import json

def lambda_handler(event, context):
    short_code = event['pathParameters']['short_code']
    
    # Simulated database lookup
    redirect_map = {
        "t65N7J": "https://www.codementor.io/blog/women-in-tech-6ev3m997u3",
        "abc123": "https://baagh.co/plants"
    }

    if short_code in redirect_map:
        return {
            "statusCode": 302,
            "headers": {
                "Location": redirect_map[short_code]
            }
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Short code not found"})
        }


```

### Notes:
- The short_code is dynamically extracted from the path using event['pathParameters']['short_code'].

- We simulate a basic redirect_map as a stand-in for a real database.

- If the short_code exists, we return a 302 redirect response with the correct Location header.

- If it does not exist, we return a 404 Not Found response with an error message.

### Using the Short Code
The short code by itself (e.g., t65N7J) is not useful alone — it needs to be part of a full URL, like:

https://bit.ly/t65N7J

https://baagh.ly/eY6p8K

https://your-own.com/E65N7J

### Testing URL
When you deploy your Lambda function and set up your API Gateway, AWS provides a default test URL (something like:
https://<random-id>.execute-api.<region>.amazonaws.com/dev/t65N7J ).

You can use this to test the redirect behavior.

Later, when you deploy your Django application, you can map your custom domain (e.g., https://baagh.ly) to your API Gateway for cleaner, branded URLs.


---



