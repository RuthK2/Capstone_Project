# Expense Tracker API

A simple REST API built with Django that helps users track their personal expenses. Users can register, login, add expenses, and view summaries of their spending.

## 🚀 Live API
**Base URL:** `https://web-production-c227c.up.railway.app`

## 📋 What You Can Do
- Register and login securely
- Add, view, update, and delete your expenses
- Organize expenses by categories (Groceries, Bills, etc.)
- **Tag expenses** for better organization (work, family, emergency)
- **Set monthly budgets** and track spending progress
- Filter expenses by time periods, categories, or tags
- Get **smart spending insights** and trend analysis
- View detailed analytics and spending summaries

## 📋 Table of Contents
- [Authentication](#authentication)
- [Budget Management](#budget-management)
- [Categories](#categories)
- [Expenses](#expenses)
- [Filtering & Analytics](#filtering--analytics)
- [Smart Insights](#smart-insights)
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
    "message": "Registration successful"
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

## 💰 Budget Management

### Set Monthly Budget
**PUT** `/api/auth/budget/`

```json
{
    "monthly_budget": "1500.00"
}
```

**Response (200 OK):**
```json
{
    "message": "Budget updated successfully",
    "monthly_budget": "1500.00"
}
```

### Get Current Budget
**GET** `/api/auth/budget/`

**Response (200 OK):**
```json
{
    "monthly_budget": "1500.00"
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
    "amount": "100.00",
    "description": "Grocery shopping at CarreFour",
    "category": 1,
    "tags": "groceries,family,weekly"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "amount": "25.50",
    "description": "Grocery shopping at Carrefour",
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

**By tags:**
- **GET** `/api/expenses/?tags=work`
- **GET** `/api/expenses/?tags=work,family`

**Combine filters:**
- **GET** `/api/expenses/?period=monthly&category=1&tags=work`

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
    "budget_status": {
        "monthly_budget": 1000.00,
        "spent": 270.50,
        "remaining": 729.50,
        "percentage_used": 27.05
    },
    "spending_insights": {
        "current_month_spending": 270.50,
        "last_month_spending": 180.00,
        "month_over_month_change": 50.28,
        "trend": "increasing",
        "top_category_this_month": "Groceries",
        "top_category_amount": 125.50
    },
    "period": "all_time"
}
```

### Summary with Filters
**GET** `/api/expenses/summary/?period=monthly`
**GET** `/api/expenses/summary/?category=1`

## 🧠 Smart Insights

### Detailed Spending Insights
**GET** `/api/expenses/insights/`

**Response (200 OK):**
```json
{
    "weekly_spending": 200.00,
    "daily_average": 28.57,
    "spending_streak_days": 3,
    "warnings": ["Groceries spending is above average"],
    "insights": [
        "You've spent money 3 days in a row",
        "Your daily average this week is $28.57",
        "Weekly spending: $200.00"
    ]
}
```

### Smart Features
- **Spending Streaks**: Track consecutive spending days
- **Category Warnings**: Alerts when spending 40% above average
- **Trend Analysis**: Month-over-month spending comparisons
- **Budget Tracking**: Real-time budget vs actual spending
- **Daily Averages**: Weekly spending patterns

## 🏷️ Expense Tags

### Using Tags
Add comma-separated tags to organize expenses:

```json
{
    "tags": "work,lunch,team"
}
```

### Filter by Tags
- Single tag: `/api/expenses/?tags=work`
- Multiple tags: `/api/expenses/?tags=work,family`
- Combined with other filters: `/api/expenses/?period=monthly&tags=emergency`

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

3. **Create your first expense with tags:**
```bash
curl -X POST https://web-production-c227c.up.railway.app/api/expenses/create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":"50.00","description":"Team lunch","category":1,"tags":"work,lunch,team"}'
```

4. **Set your monthly budget:**
```bash
curl -X PUT https://web-production-c227c.up.railway.app/api/auth/budget/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"monthly_budget":"1000.00"}'
```

5. **Get smart insights:**
```bash
curl -X GET https://web-production-c227c.up.railway.app/api/expenses/insights/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
