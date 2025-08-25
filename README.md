# Tabble-v3

A modern restaurant management system built with Python FastAPI and React, featuring QR code-based table ordering, phone OTP authentication, real-time order management, and a unified database architecture for multi-hotel operations.

## 🌟 Key Features

### 🍽️ Customer Interface
- **Phone OTP Authentication**: Secure Firebase-based authentication
- **Real-time Cart Management**: Live cart updates with special offers
- **Today's Specials**: Dynamic special dish recommendations
- **Payment Processing**: Integrated payment with loyalty discounts
- **Order History**: Track past orders and preferences

### 👨‍🍳 Chef Dashboard
- **Real-time Order Management**: Live order notifications and updates
- **Kitchen Operations**: Streamlined order acceptance and completion
- **Order Status Updates**: Instant status changes reflected across all interfaces

### 🏨 Admin Panel
- **Complete Restaurant Management**: Full control over restaurant operations
- **Dish Management**: Add, edit, and manage menu items with images
- **Offers & Specials**: Create and manage promotional offers
- **Table Management**: Monitor table occupancy and status
- **Order Tracking**: Complete order lifecycle management
- **Loyalty Program**: Configurable visit-based discount system
- **Selection Offers**: Amount-based discount configuration
- **Settings**: Hotel information and configuration management

### 📊 Analytics Dashboard
- **Customer Analysis**: Detailed customer behavior insights
- **Dish Performance**: Menu item popularity and sales metrics
- **Chef Performance**: Kitchen efficiency tracking
- **Sales & Revenue**: Comprehensive financial reporting

### 🗄️ Unified Database Architecture
- **Multi-Hotel Support**: A single database (`Tabble.db`) supports multiple independent hotel operations.
- **Data Isolation**: Data is segregated by a `hotel_id` in each table, ensuring complete privacy between establishments.
- **Centralized Management**: Hotel identities and credentials are managed in a central `hotels` table.

## 📁 Project Structure

```
tabble/
├── app/                           # Backend FastAPI application
│   ├── database.py               # Database configuration and SQLAlchemy models
│   ├── main.py                   # FastAPI application entry point
│   ├── middleware/               # Custom middleware (CORS, session handling)
│   ├── models/                   # Pydantic models for API requests/responses
│   ├── routers/                  # API route definitions
│   ├── static/                   # Static file serving (images)
│   └── utils/                    # Utility functions
├── frontend/                      # React frontend application
├── init_db.py                    # Script to initialize the database with sample data
├── requirements.txt              # Python dependencies
├── run.py                        # Backend server launcher
└── README.md                     # Project documentation
```

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **Git**

### 🔧 Installation & Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd tabble
```

#### 2. Backend Setup
```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

#### 3. Initialize the Database
This step creates the `Tabble.db` file and populates it with sample hotels and menu data for the first hotel.
```bash
python init_db.py --force-reset
```

#### 4. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

#### 5. Configure Environment Variables

##### Backend (`.env` in root directory):
Create a `.env` file in the project root with a secret key:
```env
SECRET_KEY=your_secret_key_here
```

##### Frontend (`frontend/.env`):
Create a `.env` file in the `frontend` directory. You can copy the example file: `cp .env.example .env`. The default settings should work for local development.
```env
# Backend API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000
```

## 🗄️ Database Management

### Understanding the Unified Database System

Tabble uses a **single SQLite database (`Tabble.db`)** to manage all hotels. This provides a robust and centralized way to handle data while ensuring strict data isolation between different hotel establishments.

- **Hotel Management**: Hotels are defined in the `hotels` table within `Tabble.db`. The `init_db.py` script populates this table with sample hotels to get you started.
- **Data Isolation**: Every relevant table in the database (e.g., `dishes`, `orders`, `persons`) has a `hotel_id` column. The application backend ensures that all queries are filtered by the `hotel_id` of the currently authenticated hotel, providing complete data separation.
- **Authentication**: When a user logs into a specific hotel, a session is created that is tied to that hotel's `hotel_id`. All subsequent API requests for that session will operate only on that hotel's data.

### Adding a New Hotel

Adding a new hotel must be done directly in the database by adding a new entry to the `hotels` table.

## ▶️ Running the Application

#### 1. Start Backend Server
```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Start the FastAPI server
python run.py
```
The backend will be available at `http://localhost:8000`.

#### 2. Start Frontend Development Server
```bash
# Navigate to frontend directory
cd frontend

# Start React development server
npm start
```
The frontend will be available at `http://localhost:3000`.

### 🔗 API Documentation

Once the backend is running, access the interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🚨 Troubleshooting

### Common Issues

- **Module Not Found Errors**: Ensure you have installed the backend dependencies with `pip install -r requirements.txt`.
- **Database Connection Fails**: Run `python init_db.py --force-reset` to create a fresh database with the correct schema and sample data.
- **Frontend API Calls Fail**: Verify that `REACT_APP_API_BASE_URL` in `frontend/.env` is pointing to the correct backend address (e.g., `http://localhost:8000`).
- **Database Schema Outdated**: If you pull new changes that modify the database schema, it's often best to reset the database by running `python init_db.py --force-reset`.
