## Setting Up DynamoDB for Short Code Redirection

## Problem

Until now, we were using **hardcoded values** in the Lambda function to test redirection logic for short codes.

To move towards a real-world setup, we need to store and fetch short codes from a **real database** that supports fast access.

---

## Why DynamoDB over Firebase?

We are choosing **DynamoDB** because:

- It’s **AWS native**, which makes integration with other AWS services (like Lambda) simpler.
- Easier for beginners within the AWS ecosystem.
- No extra authentication setup required like in Firebase.

---

## Steps to Set Up DynamoDB

### 1. Open DynamoDB
Go to:
**AWS Console** → **Dashboard** → **Services** → **DynamoDB**

### 2. Create a Table
- **Table Name**: e.g., `ShortLinks`
- **Partition Key (Primary Key)**: `short_code`  
  (This uniquely identifies each item)

### 3. Add Data Manually
- Use the AWS Console to **manually insert items**.
- Example item:
  ```json
  {
    "short_code": "abc123",
    "original_url": "https://baagh.co/plants"
  }

#### Next Steps:

1. #### Permissions - Lambda Access to DynamoDB (Access Control)
2. #### Update your Lambda function to query DynamoDB instead of using hardcoded values. (Read Operations):
3. #### Testing
4. #### Syncing DynamoDB with Django (Write Operations): 

Later, we will sync our Django app (SQLite) with DynamoDB by:
Automatically pushing new short code entries from Django to DynamoDB whenever a short link is created. This will ensure that Lambda has fast, real-time access to the most recent short codes.


### Architectural Insight
In larger systems:
It’s common to use different databases for different components.
In this case:
-> SQLite (Relational DB): Used by Django for full app logic, analytics, user sessions, etc.
-> DynamoDB (NoSQL): Used as a lightweight, fast-access store for public redirection.

#### Note:
Syncing happens from Django → DynamoDB. We do not sync from DynamoDB → Django because it’s rarely required in real-world architectures, adds unnecessary complexity and potential for data inconsistency.
