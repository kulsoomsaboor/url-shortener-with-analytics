## AWS Lambda
AWS Lambda is a serverless computing service that lets users define the logic (code), and AWS automatically handles the underlying infrastructure, scaling, and availability. It's called serverless because you don’t manage any servers — AWS runs your code on demand.

## API Gateway
Amazon API Gateway acts as a bridge between client requests and AWS Lambda functions. Whenever a user sends an HTTP request, the API Gateway routes it to the appropriate Lambda function based on the configured route.

Questions:

1. How does any random link on the internet route to our Lambda function?
It doesn’t happen automatically. We configure API Gateway routing rules to handle specific URLs. For example, when we define a route like: ```/{short_code}```. API Gateway will capture any request matching that pattern (e.g., /abc123) and forward it to our Lambda function.

2. What if many links have the same route pattern like /short_code? How does Lambda know where to redirect?
Even though the route pattern is the same (/{short_code}), the actual value of short_code (e.g., abc123, xyz789) is dynamic. Lambda receives this value as an event path parameter, then looks it up in the database (like DynamoDB). If it finds a match, it redirects the user to the corresponding original URL stored for that short code.


Lambda only responds with redirection logic — actual HTTP redirection (like a 301 or 302 status) is returned to the client by Lambda through the API Gateway.

