# Tabble-v3

A modern restaurant management system built with Python FastAPI and React, featuring QR code-based table ordering, phone OTP authentication, real-time order management, and a unified database architecture for multi-hotel operations.

## 🌟 Key Features

- **Customer Interface**: QR code ordering, real-time cart, special offers, and loyalty tracking.
- **Chef Dashboard**: Real-time order management and kitchen operations.
- **Admin Panel**: Full control over a hotel's operations, including dish management, offers, tables, and settings.
- **Analytics Dashboard**: Insights into customer behavior, dish performance, and sales.
- **Unified Database**: A single database supports multiple independent hotel operations with full data isolation.
- **Master Admin**: A secure, hidden interface for creating and managing hotels.

## 📁 Project Structure

```
tabble/
├── app/                           # Backend FastAPI application
│   ├── auth.py                   # Master password authentication dependency
│   ├── database.py               # Database configuration and SQLAlchemy models
│   ├── main.py                   # FastAPI application entry point
│   ├── models/                   # Pydantic models for API requests/responses
│   └── routers/                  # API route definitions (customer, chef, admin, master)
├── frontend/                      # React frontend application
├── init_db.py                    # Script to initialize the database with sample data
├── .env                          # Local environment variables (create this)
├── .env.example                  # Example environment variables
├── requirements.txt              # Python dependencies
├── run.py                        # Backend server launcher
└── README.md                     # Project documentation
```

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### 🔧 Installation & Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd tabble
```

#### 2. Configure Environment Variables
Create a `.env` file in the project root by copying the example:
```bash
cp .env.example .env
```
Now, open the `.env` file and set the following variables:
```env
SECRET_KEY=a_very_secret_key_that_you_should_change
MASTER_PASSWORD=a_secure_master_password_of_your_choice
```

#### 3. Backend Setup
```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

#### 4. Initialize the Database
This step creates the `Tabble.db` file and populates it with a sample hotel and menu data.
```bash
python init_db.py --force-reset
```

#### 5. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```
The frontend is pre-configured to connect to `http://localhost:8000`.

## ▶️ Running the Application

#### 1. Start Backend Server
```bash
# Make sure your virtual environment is activated
python run.py
```
The backend will be available at `http://localhost:8000`.

#### 2. Start Frontend Development Server
```bash
# Navigate to frontend directory
cd frontend
npm start
```
The frontend will be available at `http://localhost:3000`.

## 🗄️ Hotel & Database Management

### Unified Database System
Tabble uses a **single SQLite database (`Tabble.db`)** to manage all hotels. This provides a robust and centralized way to handle data while ensuring strict data isolation between different hotel establishments using a `hotel_id` on all relevant data.

### Master Admin for Hotel Management
All hotel creation and management is handled through a secure, hidden master admin panel.

1.  **Set the Master Password**: Ensure the `MASTER_PASSWORD` is set in your `.env` file as described in the setup instructions.
2.  **Access the Panel**: Navigate your browser directly to `http://localhost:3000/master-admin`. This route is not linked anywhere in the UI.
3.  **Authenticate**: Use the master password you set to log in.
4.  **Manage Hotels**: From this panel, you can create new hotels, view existing ones, and update their passwords.

### 🔗 API Documentation
Once the backend is running, access the interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

The `/master` endpoints in the documentation are protected and require the `X-Master-Password` header to be set.
