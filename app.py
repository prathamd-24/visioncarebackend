from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Supabase configuration
SUPABASE_URL = "https://ubmfikxfcupqhpwtuctl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVibWZpa3hmY3VwcWhwd3R1Y3RsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzE0MzkxMCwiZXhwIjoyMDc4NzE5OTEwfQ.6wgNifeuiuLDG9tXFalEsuBnllvL_4BJBlJb5If1U0g"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Health endpoint
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "API is running",
        "timestamp": datetime.now().isoformat()
    }), 200


# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    """
    Login endpoint - authenticates user with email and password
    Expected JSON body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                "error": "Email and password are required"
            }), 400
        
        email = data['email']
        password = data['password']
        
        # Query user from database
        response = supabase.table('users').select('*').eq('email', email).eq('password', password).execute()
        
        if not response.data or len(response.data) == 0:
            return jsonify({
                "error": "Invalid credentials"
            }), 401
        
        user = response.data[0]
        
        return jsonify({
            "message": "Login successful",
            "user_id": user['user_id'],
            "email": user['email']
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# Data insert endpoint
@app.route('/data', methods=['POST'])
def insert_data():
    """
    Insert sensor data endpoint
    Expected JSON body:
    {
        "client_id": 1,
        "avg_blink_rate": 15,
        "avg_temp": 36,
        "left_eye_redness": 5,
        "right_eye_redness": 4
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['client_id', 'avg_blink_rate', 'avg_temp', 'left_eye_redness', 'right_eye_redness']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Get the max ID from existing data and increment
        existing_data = supabase.table('data').select('id').order('id', desc=True).limit(1).execute()
        
        # Generate new ID
        if existing_data.data and len(existing_data.data) > 0:
            new_id = existing_data.data[0]['id'] + 1
        else:
            new_id = 1
        
        # Insert data into database
        response = supabase.table('data').insert({
            "id": new_id,
            "client_id": data['client_id'],
            "avg_blink_rate": data['avg_blink_rate'],
            "avg_temp": data['avg_temp'],
            "left_eye_redness": data['left_eye_redness'],
            "right_eye_redness": data['right_eye_redness']
        }).execute()
        
        return jsonify({
            "message": "Data inserted successfully",
            "data": response.data
        }), 201
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# Get data endpoint
@app.route('/data/<int:client_id>', methods=['GET'])
def get_data(client_id):
    """
    Get sensor data for a specific client
    Query parameters:
    - range: 'day', 'week', 'month', 'all' (default: 'all')
    - start_date: ISO format date (YYYY-MM-DD)
    - end_date: ISO format date (YYYY-MM-DD)
    
    Examples:
    - /data/1?range=day (last 24 hours)
    - /data/1?range=week (last 7 days)
    - /data/1?range=month (last 30 days)
    - /data/1?range=all (all data)
    - /data/1?start_date=2025-01-01&end_date=2025-01-31 (custom range)
    """
    try:
        # Get query parameters
        range_type = request.args.get('range', 'all')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Base query
        query = supabase.table('data').select('*').eq('client_id', client_id)
        
        # Apply date filters based on range or custom dates
        if start_date and end_date:
            # Custom date range
            query = query.gte('created_at', start_date).lte('created_at', end_date)
        elif range_type != 'all':
            # Predefined ranges
            now = datetime.now()
            
            if range_type == 'day':
                start = now - timedelta(days=1)
            elif range_type == 'week':
                start = now - timedelta(weeks=1)
            elif range_type == 'month':
                start = now - timedelta(days=30)
            else:
                return jsonify({
                    "error": "Invalid range type. Use 'day', 'week', 'month', or 'all'"
                }), 400
            
            query = query.gte('created_at', start.isoformat())
        
        # Execute query with ordering
        response = query.order('created_at', desc=True).execute()
        
        return jsonify({
            "client_id": client_id,
            "count": len(response.data),
            "data": response.data
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ==================== USER CRUD ENDPOINTS ====================

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    try:
        response = supabase.table('users').select('*').eq('user_id', user_id).execute()
        
        if not response.data:
            return jsonify({'error': 'User not found'}), 404
        
        # Remove password from response for security
        user_data = response.data[0]
        user_data.pop('password', None)
        
        return jsonify({
            'message': 'User retrieved successfully',
            'user': user_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user by ID"""
    try:
        data = request.get_json()
        
        # Check if user exists
        check_response = supabase.table('users').select('*').eq('user_id', user_id).execute()
        if not check_response.data:
            return jsonify({'error': 'User not found'}), 404
        
        # Prepare update data (only allow email and password updates)
        update_data = {}
        if 'email' in data:
            update_data['email'] = data['email']
        if 'password' in data:
            update_data['password'] = data['password']
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update user
        response = supabase.table('users').update(update_data).eq('user_id', user_id).execute()
        
        # Remove password from response
        result_data = response.data[0] if response.data else {}
        result_data.pop('password', None)
        
        return jsonify({
            'message': 'User updated successfully',
            'user': result_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user by ID"""
    try:
        # Check if user exists
        check_response = supabase.table('users').select('*').eq('user_id', user_id).execute()
        if not check_response.data:
            return jsonify({'error': 'User not found'}), 404
        
        # Delete user (this will also delete related data due to foreign key)
        supabase.table('users').delete().eq('user_id', user_id).execute()
        
        return jsonify({
            'message': 'User deleted successfully',
            'user_id': user_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== DATA CRUD ENDPOINTS ====================

@app.route('/data/record/<int:data_id>', methods=['GET'])
def get_data_record(data_id):
    """Get a specific data record by ID"""
    try:
        response = supabase.table('data').select('*').eq('id', data_id).execute()
        
        if not response.data:
            return jsonify({'error': 'Data record not found'}), 404
        
        return jsonify({
            'message': 'Data record retrieved successfully',
            'data': response.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/data/record/<int:data_id>', methods=['PUT'])
def update_data_record(data_id):
    """Update a specific data record by ID"""
    try:
        data = request.get_json()
        
        # Check if record exists
        check_response = supabase.table('data').select('*').eq('id', data_id).execute()
        if not check_response.data:
            return jsonify({'error': 'Data record not found'}), 404
        
        # Prepare update data (only allow specific fields)
        update_data = {}
        allowed_fields = ['avg_blink_rate', 'avg_temp', 'left_eye_redness', 'right_eye_redness']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update record
        response = supabase.table('data').update(update_data).eq('id', data_id).execute()
        
        return jsonify({
            'message': 'Data record updated successfully',
            'data': response.data[0] if response.data else {}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/data/record/<int:data_id>', methods=['DELETE'])
def delete_data_record(data_id):
    """Delete a specific data record by ID"""
    try:
        # Check if record exists
        check_response = supabase.table('data').select('*').eq('id', data_id).execute()
        if not check_response.data:
            return jsonify({'error': 'Data record not found'}), 404
        
        # Delete record
        supabase.table('data').delete().eq('id', data_id).execute()
        
        return jsonify({
            'message': 'Data record deleted successfully',
            'data_id': data_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
