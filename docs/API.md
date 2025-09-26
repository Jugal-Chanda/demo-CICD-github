# API Documentation

Complete API documentation for the Demo Flask Application.

## Table of Contents
- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
- [Rate Limiting](#rate-limiting)
- [Versioning](#versioning)

## Overview

The Demo Flask Application provides a RESTful API for user management operations. The API follows REST conventions and returns JSON responses.

### Features
- RESTful design
- JSON request/response format
- Comprehensive error handling
- Input validation
- Pagination support
- CORS enabled

## Base URL

```
Production: https://your-domain.com
Development: http://localhost:5000
Staging: https://staging.your-domain.com
```

All API endpoints are prefixed with `/api` and currently use version `v1`.

## Authentication

Currently, the API does not require authentication for demonstration purposes. In production, implement one of the following:

### Future Authentication Methods
- **JWT Bearer Token**
  ```
  Authorization: Bearer <jwt_token>
  ```

- **API Key**
  ```
  X-API-Key: <api_key>
  ```

- **Basic Authentication**
  ```
  Authorization: Basic <base64_credentials>
  ```

## Response Format

All API responses follow a consistent JSON structure:

### Success Response
```json
{
  "success": true,
  "data": <response_data>,
  "message": "Optional success message",
  "timestamp": "2025-01-19T10:30:00.000Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "field": "field_name_if_applicable",
  "timestamp": "2025-01-19T10:30:00.000Z"
}
```

### List Response
```json
{
  "success": true,
  "data": [
    <item1>,
    <item2>
  ],
  "count": 2,
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "total_pages": 3
  }
}
```

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 405 | Method Not Allowed | HTTP method not supported |
| 409 | Conflict | Resource conflict (e.g., duplicate email) |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `MISSING_REQUIRED_FIELD` | 400 | Required field is missing |
| `INVALID_EMAIL_FORMAT` | 400 | Email format is invalid |
| `DUPLICATE_EMAIL` | 409 | Email already exists |
| `USER_NOT_FOUND` | 404 | User does not exist |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `SERVICE_UNAVAILABLE` | 503 | External service unavailable |

### Validation Errors

Validation errors include field-specific information:

```json
{
  "success": false,
  "error": "Email format is invalid",
  "code": "VALIDATION_ERROR",
  "field": "email",
  "timestamp": "2025-01-19T10:30:00.000Z"
}
```

## Endpoints

### Health Check

Get application health status.

```http
GET /
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-01-19T10:30:00.000Z",
    "version": "1.0.0",
    "database": "connected",
    "uptime": "1h 30m"
  }
}
```

**Response (500 Internal Server Error):**
```json
{
  "success": false,
  "error": "Service unhealthy",
  "code": "SERVICE_UNAVAILABLE",
  "details": {
    "database": "disconnected",
    "timestamp": "2025-01-19T10:30:00.000Z"
  }
}
```

---

### List Users

Retrieve a paginated list of users.

```http
GET /api/users
```

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `per_page` (integer, optional): Items per page (default: 10, max: 100)
- `sort_by` (string, optional): Sort field (default: created_at)
- `sort_order` (string, optional): Sort order (asc/desc, default: desc)

**Example Request:**
```http
GET /api/users?page=1&per_page=5&sort_by=name&sort_order=asc
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Alice Brown",
      "email": "alice@example.com",
      "age": 28,
      "created_at": "2025-01-19T09:00:00.000Z",
      "updated_at": "2025-01-19T09:00:00.000Z"
    },
    {
      "id": 2,
      "name": "Bob Johnson",
      "email": "bob@example.com",
      "age": 35,
      "created_at": "2025-01-19T09:15:00.000Z",
      "updated_at": "2025-01-19T09:15:00.000Z"
    }
  ],
  "count": 2,
  "pagination": {
    "page": 1,
    "per_page": 5,
    "total": 25,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### Create User

Create a new user.

```http
POST /api/users
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "age": 30
}
```

**Field Requirements:**

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `name` | string | Yes | 2-100 characters |
| `email` | string | Yes | Valid email format, unique |
| `age` | integer | No | 0-150 (optional) |

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 3,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "age": 30,
    "created_at": "2025-01-19T10:30:00.000Z",
    "updated_at": "2025-01-19T10:30:00.000Z"
  },
  "message": "User created successfully"
}
```

**Error Responses:**

*Missing required field:*
```json
HTTP/1.1 400 Bad Request
{
  "success": false,
  "error": "name is required",
  "code": "VALIDATION_ERROR",
  "field": "name"
}
```

*Invalid email format:*
```json
HTTP/1.1 400 Bad Request
{
  "success": false,
  "error": "Invalid email format",
  "code": "VALIDATION_ERROR",
  "field": "email"
}
```

*Duplicate email:*
```json
HTTP/1.1 409 Conflict
{
  "success": false,
  "error": "Email already exists",
  "code": "DUPLICATE_EMAIL",
  "field": "email"
}
```

---

### Get User by ID

Retrieve a specific user by ID.

```http
GET /api/users/{id}
```

**Path Parameters:**
- `id` (integer): User ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Alice Brown",
    "email": "alice@example.com",
    "age": 28,
    "created_at": "2025-01-19T09:00:00.000Z",
    "updated_at": "2025-01-19T09:00:00.000Z"
  }
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "error": "User not found",
  "code": "USER_NOT_FOUND"
}
```

---

### Update User

Update an existing user.

```http
PUT /api/users/{id}
Content-Type: application/json
```

**Path Parameters:**
- `id` (integer): User ID

**Request Body:**
```json
{
  "name": "Alice Smith",
  "email": "alice.smith@example.com",
  "age": 29
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice.smith@example.com",
    "age": 29,
    "created_at": "2025-01-19T09:00:00.000Z",
    "updated_at": "2025-01-19T10:45:00.000Z"
  },
  "message": "User updated successfully"
}
```

---

### Delete User

Delete a user.

```http
DELETE /api/users/{id}
```

**Path Parameters:**
- `id` (integer): User ID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

### Bulk Operations

#### Bulk Create Users

```http
POST /api/users/bulk
Content-Type: application/json
```

**Request Body:**
```json
{
  "users": [
    {
      "name": "User 1",
      "email": "user1@example.com",
      "age": 25
    },
    {
      "name": "User 2",
      "email": "user2@example.com",
      "age": 30
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "created": 2,
    "failed": 0,
    "users": [
      {
        "id": 4,
        "name": "User 1",
        "email": "user1@example.com",
        "age": 25
      },
      {
        "id": 5,
        "name": "User 2",
        "email": "user2@example.com",
        "age": 30
      }
    ]
  }
}
```

## Rate Limiting

API rate limiting is implemented to prevent abuse:

- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour
- **Burst limit**: 50 requests per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640995200
X-RateLimit-Retry-After: 3600 (only when limit exceeded)
```

## Versioning

The API uses URL path versioning:

- **Current version**: v1
- **Version format**: `/api/v1/resource`

Future versions will be:
- `/api/v2/resource`

### Version Compatibility

- **v1**: Current stable version
- **Breaking changes**: Will be introduced in v2
- **Deprecation**: v1 will be supported for 12 months after v2 release

### Version Headers

Clients can specify API version in requests:

```
Accept: application/vnd.api.v1+json
```

## SDKs and Libraries

### Python Client

```python
import requests

class DemoAPIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def get_users(self, page=1, per_page=10):
        response = self.session.get(f"{self.base_url}/api/users",
                                  params={"page": page, "per_page": per_page})
        return response.json()

    def create_user(self, user_data):
        response = self.session.post(f"{self.base_url}/api/users",
                                   json=user_data)
        return response.json()

# Usage
client = DemoAPIClient()
users = client.get_users()
new_user = client.create_user({
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
})
```

### JavaScript Client

```javascript
class DemoAPIClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }

    async getUsers(page = 1, perPage = 10) {
        const response = await fetch(`${this.baseURL}/api/users?page=${page}&per_page=${perPage}`);
        return response.json();
    }

    async createUser(userData) {
        const response = await fetch(`${this.baseURL}/api/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });
        return response.json();
    }
}

// Usage
const client = new DemoAPIClient();
client.getUsers().then(data => console.log(data));
```

## Webhooks

The API supports webhooks for real-time notifications:

### Webhook Configuration

```http
POST /api/webhooks
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": ["user.created", "user.updated", "user.deleted"],
  "secret": "your-webhook-secret"
}
```

### Webhook Events

- `user.created`: Fired when a new user is created
- `user.updated`: Fired when a user is updated
- `user.deleted`: Fired when a user is deleted

### Webhook Payload

```json
{
  "event": "user.created",
  "timestamp": "2025-01-19T10:30:00.000Z",
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30
    }
  },
  "signature": "sha256=..."
}
```

## Monitoring

### API Metrics

The API exposes Prometheus metrics at `/metrics`:

```
# HELP api_requests_total Total number of API requests
# TYPE api_requests_total counter
api_requests_total{method="GET",endpoint="/api/users",status="200"} 150

# HELP api_request_duration_seconds Request duration in seconds
# TYPE api_request_duration_seconds histogram
api_request_duration_seconds_bucket{method="GET",endpoint="/api/users",le="0.1"} 140
```

### Health Checks

Comprehensive health checks are available at `/health`:

```json
{
  "status": "healthy",
  "checks": {
    "database": "healthy",
    "cache": "healthy",
    "external_services": "healthy"
  },
  "timestamp": "2025-01-19T10:30:00.000Z"
}
```

## Changelog

### Version 1.0.0
- Initial API release
- User CRUD operations
- Basic authentication framework
- Rate limiting
- Comprehensive error handling

### Planned Features (v2.0.0)
- Advanced filtering and search
- User roles and permissions
- File upload support
- GraphQL API
- Real-time notifications with WebSocket

## Support

For API support and questions:
- **Documentation**: https://api.your-domain.com/docs
- **Status Page**: https://status.your-domain.com
- **Support Email**: api-support@your-domain.com
- **Community Forum**: https://community.your-domain.com

## Terms of Service

By using this API, you agree to:
1. Respect rate limits
2. Handle errors gracefully
3. Keep API keys secure
4. Use HTTPS in production
5. Monitor your usage

See [Terms of Service](https://your-domain.com/terms) for complete details.