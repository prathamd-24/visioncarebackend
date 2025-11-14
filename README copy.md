# Flask Supabase API

A Flask REST API with Supabase integration for managing user authentication and sensor data.

## Features

- ✅ CORS enabled for all routes
- ✅ Supabase database integration
- ✅ User authentication
- ✅ Sensor data management
- ✅ Flexible data retrieval (by range, day, custom dates)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```

### Data Table
```sql
CREATE TABLE data (
    id INT PRIMARY KEY,
    client_id INT,
    avg_blink_rate INT,
    avg_temp INT,
    left_eye_redness INT,
    right_eye_redness INT,
    created_at timestamp with time zone not null default now(),
    FOREIGN KEY (client_id) REFERENCES users(user_id)
);
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The API will start on `http://localhost:5000`

## API Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
    "status": "healthy",
    "message": "API is running",
    "timestamp": "2025-11-14T10:30:00"
}
```

### 2. Login
**POST** `/login`

Authenticate a user with email and password.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "message": "Login successful",
    "user_id": 1,
    "email": "user@example.com"
}
```

---

## User Management Endpoints

### 3. Get User
**GET** `/users/<user_id>`

Get user details by user ID (password excluded from response).

**Response:**
```json
{
    "message": "User retrieved successfully",
    "user": {
        "user_id": 1,
        "email": "user@example.com"
    }
}
```

### 4. Update User
**PUT** `/users/<user_id>`

Update user email or password.

**Request Body:**
```json
{
    "email": "newemail@example.com",
    "password": "newpassword123"
}
```

**Response:**
```json
{
    "message": "User updated successfully",
    "user": {
        "user_id": 1,
        "email": "newemail@example.com"
    }
}
```

### 5. Delete User
**DELETE** `/users/<user_id>`

Delete a user by ID.

**Response:**
```json
{
    "message": "User deleted successfully",
    "user_id": 1
}
```

---

## Data Management Endpoints

### 6. Insert Data
**POST** `/data`

Insert sensor data for a client.

**Request Body:**
```json
{
    "client_id": 1,
    "avg_blink_rate": 15,
    "avg_temp": 36,
    "left_eye_redness": 5,
    "right_eye_redness": 4
}
```

**Response:**
```json
{
    "message": "Data inserted successfully",
    "data": [...]
}
```

### 7. Get Data by Client
**GET** `/data/<client_id>`

Retrieve sensor data for a specific client with optional filtering.

**Query Parameters:**
- `range`: `day` (last 24h), `week` (last 7 days), `month` (last 30 days), `all` (default)
- `start_date`: Custom start date (YYYY-MM-DD)
- `end_date`: Custom end date (YYYY-MM-DD)

**Examples:**
```bash
# Get all data for client 1
GET /data/1?range=all

# Get last 24 hours
GET /data/1?range=day

# Get last week
GET /data/1?range=week

# Get last month
GET /data/1?range=month

# Custom date range
GET /data/1?start_date=2025-01-01&end_date=2025-01-31
```

**Response:**
```json
{
    "client_id": 1,
    "count": 10,
    "data": [
        {
            "id": 1,
            "client_id": 1,
            "avg_blink_rate": 15,
            "avg_temp": 36,
            "left_eye_redness": 5,
            "right_eye_redness": 4,
            "created_at": "2025-11-14T10:30:00"
        }
    ]
}
```

### 8. Get Single Data Record
**GET** `/data/record/<data_id>`

Get a specific data record by its ID.

**Response:**
```json
{
    "message": "Data record retrieved successfully",
    "data": {
        "id": 1,
        "client_id": 1,
        "avg_blink_rate": 15,
        "avg_temp": 36,
        "left_eye_redness": 5,
        "right_eye_redness": 4,
        "created_at": "2025-11-14T10:30:00"
    }
}
```

### 9. Update Data Record
**PUT** `/data/record/<data_id>`

Update a specific data record.

**Request Body:**
```json
{
    "avg_blink_rate": 18,
    "avg_temp": 37,
    "left_eye_redness": 6,
    "right_eye_redness": 5
}
```

**Response:**
```json
{
    "message": "Data record updated successfully",
    "data": {
        "id": 1,
        "client_id": 1,
        "avg_blink_rate": 18,
        "avg_temp": 37,
        "left_eye_redness": 6,
        "right_eye_redness": 5,
        "created_at": "2025-11-14T10:30:00"
    }
}
```

### 10. Delete Data Record
**DELETE** `/data/record/<data_id>`

Delete a specific data record.

**Response:**
```json
{
    "message": "Data record deleted successfully",
    "data_id": 1
}
```

## Testing with curl

### Authentication & Health
```bash
# Health check
curl http://localhost:5000/health

# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test_user@example.com","password":"test123"}'
```

### User Management
```bash
# Get user by ID
curl http://localhost:5000/users/999

# Update user
curl -X PUT http://localhost:5000/users/999 \
  -H "Content-Type: application/json" \
  -d '{"email":"updated@example.com","password":"newpass123"}'

# Delete user
curl -X DELETE http://localhost:5000/users/999
```

### Data Management
```bash
# Insert data
curl -X POST http://localhost:5000/data \
  -H "Content-Type: application/json" \
  -d '{"client_id":999,"avg_blink_rate":15,"avg_temp":36,"left_eye_redness":5,"right_eye_redness":4}'

# Get data by client (all)
curl http://localhost:5000/data/999?range=all

# Get data by client (last day)
curl http://localhost:5000/data/999?range=day

# Get data (custom range)
curl "http://localhost:5000/data/999?start_date=2025-01-01&end_date=2025-01-31"

# Get single data record
curl http://localhost:5000/data/record/1

# Update data record
curl -X PUT http://localhost:5000/data/record/1 \
  -H "Content-Type: application/json" \
  -d '{"avg_blink_rate":20,"avg_temp":37,"left_eye_redness":6,"right_eye_redness":5}'

# Delete data record
curl -X DELETE http://localhost:5000/data/record/1
```

## Configuration

The Supabase URL and API key are configured in `app.py`. For production, consider using environment variables:

```python
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
```

## Security Notes

⚠️ **Important**: 
- This implementation stores passwords in plain text. For production, use bcrypt or similar hashing.
- Consider using JWT tokens for authentication instead of sending credentials on every request.
- Move sensitive credentials to environment variables.
