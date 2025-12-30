# Expense Tracker API

A simple REST API built with Django that helps users track their personal expenses. Users can register, login, add expenses, and view summaries of their spending.

## 🚀 Live API
**Base URL:** `https://web-production-c227c.up.railway.app`

## 📋 What You Can Do
- Register and login securely
- Add, view, update, and delete your expenses
- Organize expenses by categories (Groceries, Bills, etc.)
- Filter expenses by time periods or categories
- Get spending summaries and analytics

## 📋 Table of Contents
- [Authentication](#authentication)
- [Categories](#categories)
- [Expenses](#expenses)
- [Filtering & Analytics](#filtering--analytics)
- [Error Handling](#error-handling)
- [Technology Stack](#technology-stack)

## 🔐 Authentication

To use most features, you need to register and login first. The API uses JWT tokens for security.

**How to authenticate:**
```
Authorization: Bearer <your_access_token>
```

### Register User
**POST** `/api/auth/register/`

```json
{
    "username": "newuser",
    "email": "new@example.com",
    "password": "newpass123"
}
```

**Response (201 Created):**
```json
{
    "user": {
        "id": 1,
        "username": "newuser",
        "email": "new@example.com"
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Login
**POST** `/api/auth/login/`

```json
{
    "username": "testuser",
    "password": "testpass123"
}
```

**Response (200 OK):**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refresh Token
**POST** `/api/auth/token/refresh/`

```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Logout
**POST** `/api/auth/logout/`

**Response (200 OK):**
```json
{
    "message": "Logout successful"
}
```

## 📂 Categories

### List Categories
**GET** `/api/categories/`

**Response (200 OK):**
```json
{
    "count": 6,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Groceries",
            "description": ""
        },
        {
            "id": 2,
            "name": "Electricity",
            "description": ""
        },
        {
            "id": 3,
            "name": "Utilities",
            "description": ""
        },
        {
            "id": 4,
            "name": "Miscellaneous",
            "description": ""
        },
        {
            "id": 5,
            "name": "Electronics",
            "description": ""
        },
        {
            "id": 6,
            "name": "Clothing",
            "description": ""
        }
    ]
}
```

## 💰 Expenses

### Create Expense
**POST** `/api/expenses/create/`

```json
{
    "amount": "25.50",
    "description": "Grocery shopping at Cleanshelf",
    "category": 1
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "amount": "25.50",
    "description": "Grocery shopping at Naivas",
    "category": {
        "id": 1,
        "name": "Groceries"
    },
    "date": "2024-01-15",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### List Expenses
**GET** `/api/expenses/`

**Response (200 OK):**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 2,
            "amount": "45.00",
            "description": "Electric bill payment",
            "category": {
                "id": 2,
                "name": "Electricity"
            },
            "date": "2024-01-15",
            "timestamp": "2024-01-15T14:20:00Z"
        },
        {
            "id": 1,
            "amount": "25.50",
            "description": "Grocery shopping at Walmart",
            "category": {
                "id": 1,
                "name": "Groceries"
            },
            "date": "2024-01-15",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### Update Expense
**PUT** `/api/expenses/{id}/update/`

```json
{
    "amount": "30.00",
    "description": "Updated grocery shopping",
    "category": 1
}
```

### Delete Expense
**DELETE** `/api/expenses/{id}/delete/`

**Response (204 No Content)**

## 📊 Filtering & Analytics

### Filter Your Expenses
**By time period:**
- **GET** `/api/expenses/?period=weekly`
- **GET** `/api/expenses/?period=monthly`
- **GET** `/api/expenses/?period=last_3_months`

**By category:**
- **GET** `/api/expenses/?category=1`

**Combine filters:**
- **GET** `/api/expenses/?period=monthly&category=1`

### Expense Summary
**GET** `/api/expenses/summary/`

**Response (200 OK):**
```json
{
    "summary": {
        "total_amount": 270.50,
        "total_count": 5,
        "average_amount": 54.10
    },
    "category_breakdown": [
        {
            "name": "Groceries",
            "total": 125.50,
            "count": 3,
            "percentage": 46.40
        },
        {
            "name": "Electricity",
            "total": 85.00,
            "count": 1,
            "percentage": 31.42
        },
        {
            "name": "Utilities",
            "total": 60.00,
            "count": 1,
            "percentage": 22.18
        }
    ],
    "period": "all_time"
}
```

### Summary with Filters
**GET** `/api/expenses/summary/?period=monthly`
**GET** `/api/expenses/summary/?category=1`

## 📄 Pagination

All list endpoints support pagination:
- `?page=2` - Get page 2
- `?page_size=10` - Set items per page (max 100)

**Example:** `/api/expenses/?page=2&page_size=10`

## ❌ Error Handling

### Authentication Errors
```json
{
    "error": "Authentication credentials were not provided."
}
```

### Validation Errors
```json
{
    "error": {
        "amount": ["This field is required."],
        "category": ["Invalid pk \"999\" - object does not exist."]
    }
}
```

### Not Found Errors
```json
{
    "error": "Expense not found."
}
```

## 🛠 Technology Stack
- **Backend:** Django (Python web framework)
- **Database:** SQLite
- **Authentication:** JWT tokens
- **API:** Django REST Framework
- **Deployment:** Railway

## 🔗 Quick Start

1. **Register a new account:**
```bash
curl -X POST https://web-production-c227c.up.railway.app/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"myuser","email":"my@email.com","password":"mypass123"}'
```

2. **Login to get access token:**
```bash
curl -X POST https://web-production-c227c.up.railway.app/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"myuser","password":"mypass123"}'
```

3. **Create your first expense:**
```bash
curl -X POST https://web-production-c227c.up.railway.app/api/expenses/create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":"50.00","description":"Lunch","category":1}'
```
