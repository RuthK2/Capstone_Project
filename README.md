# Expense Tracker API

A REST API built with Django and Django REST Framework that helps users manage their personal finances by tracking expenses.

## Core Functionalities

### 1. User Authentication
- Register new accounts with secure credentials
- Login with JWT token-based authentication
- Logout functionality

### 2. Expense Management
- Create new expense entries with amount, description, and category
- View all your expenses
- Update existing expense details
- Delete expenses you no longer need

### 3. Category Organization
- Organize expenses into predefined categories: Groceries, Electricity, Utilities, Miscellaneous, Electronics, and Clothing
- View expenses by specific categories

### 4. Filtering & Analytics
- Filter expenses by time periods (weekly, monthly, last 3 months)
- Filter expenses by category
- Get expense summaries and insights

## Technology Stack
- Backend: Django with Django REST Framework
- Database: PostgreSQL/SQLite
- Authentication: JWT (djangorestframework-simplejwt)
