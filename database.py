import streamlit as st
import psycopg2
import psycopg2.extras
import json
from datetime import datetime
import os
import uuid
import hashlib
from dotenv import load_dotenv


# Initialize connection to the PostgreSQL database
# Using cache_resource to maintain a single connection for reuse
@st.cache_resource
def init_connection():
    try:
        # Directly use the correct PostgreSQL connection string
        database_url = "postgresql://postgres:skandarDZ123@localhost:3000/postgres"

        conn = psycopg2.connect(database_url)
        conn.autocommit = False  # Ensure explicit transactions
        return conn
    except Exception as e:
        st.error(f"Error connecting to PostgreSQL database: {e}")
        return None

# Get a new connection for each query to avoid "connection already closed" errors
def get_connection():
    try:
        database_url = "postgresql://postgres:skandarDZ123@localhost:3000/postgres"

        conn = psycopg2.connect(database_url)
        conn.autocommit = False  # Ensure explicit transactions
        return conn
    except Exception as e:
        st.error(f"Error connecting to PostgreSQL database: {e}")
        return None

# Execute a SELECT query and return the results
def execute_query(query, params=None):
    conn = get_connection()  # Get a fresh connection for each query
    if conn is None:
        return None

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in results]
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Execute an INSERT, UPDATE, or DELETE query
def execute_update(query, params=None):
    conn = get_connection()  # Get a fresh connection for each update
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        return affected_rows > 0
    except Exception as e:
        st.error(f"Error executing update: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Function to check user credentials
def check_user_credentials(username, hashed_password):
    query = """
    SELECT * FROM users
    WHERE username = %s AND password = %s
    """
    params = (username, hashed_password)
    results = execute_query(query, params)
    
    if results and len(results) > 0:
        return results[0]
    return None

# Function to check if username exists
def check_username_exists(username):
    query = """
    SELECT * FROM users
    WHERE username = %s
    """
    params = (username,)
    results = execute_query(query, params)
    
    return results and len(results) > 0

# Function to register a new user
def register_user(username, email, hashed_password, field):
    # Set status to 'pending' for new users
    query = """
    INSERT INTO users (username, email, password, field, role, status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (username, email, hashed_password, field, 'user', 'pending', datetime.now())
    
    return execute_update(query, params)

# Function to update user status
def update_user_status(username, status):
    query = """
    UPDATE users
    SET status = %s
    WHERE username = %s
    """
    params = (status, username)
    
    return execute_update(query, params)

# Function to get users by status
def get_users_by_status(status):
    query = """
    SELECT username, email, field, role, status, created_at
    FROM users
    WHERE status = %s
    """
    params = (status,)
    
    return execute_query(query, params)

# Function to get user data
def get_user_data(username):
    query = """
    SELECT username, email, field, role, status, created_at
    FROM users
    WHERE username = %s
    """
    params = (username,)
    results = execute_query(query, params)
    
    if results and len(results) > 0:
        return results[0]
    return None

# Function to save KPI data
def save_kpi_data(kpi_data):
    # Convert the data to a format suitable for PostgreSQL
    # We'll store specific fields and then the rest as JSON in a data column
    username = kpi_data.pop("username")
    field = kpi_data.pop("field")
    date = kpi_data.pop("date")
    process_name = kpi_data.pop("process_name", "Unknown Process")
    
    # Serialize the remaining data as JSON
    data_json = json.dumps(kpi_data)
    
    query = """
    INSERT INTO kpi_data (username, field, date, process_name, data)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (username, field, date, process_name, data_json)
    
    return execute_update(query, params)

# Function to get KPI data for a user
def get_user_kpi_data(username):
    query = """
    SELECT username, field, date, process_name, data
    FROM kpi_data
    WHERE username = %s
    ORDER BY date
    """
    params = (username,)
    results = execute_query(query, params)
    
    if not results:
        return []
    
    # Process the results to unpack the JSON data
    processed_results = []
    for row in results:
        # Handle JSON data based on its type
        if isinstance(row["data"], str):
            # If it's a string, parse it
            data_dict = json.loads(row["data"])
        elif isinstance(row["data"], dict):
            # If it's already a dict, use it directly
            data_dict = row["data"]
        else:
            # Skip invalid data
            continue
        
        # Create a new row with unpacked data
        new_row = {
            "username": row["username"],
            "field": row["field"],
            "date": row["date"],
            "process_name": row["process_name"],
            **data_dict  # Unpack all KPI fields
        }
        
        processed_results.append(new_row)
    
    return processed_results

# Function to get all KPI data
def get_all_kpi_data():
    query = """
    SELECT k.username, k.field, k.date, k.process_name, k.data, u.role
    FROM kpi_data k
    JOIN users u ON k.username = u.username
    ORDER BY k.date
    """
    results = execute_query(query)
    
    if not results:
        return []
    
    # Process the results to unpack the JSON data
    processed_results = []
    for row in results:
        # Handle JSON data based on its type
        if isinstance(row["data"], str):
            # If it's a string, parse it
            data_dict = json.loads(row["data"])
        elif isinstance(row["data"], dict):
            # If it's already a dict, use it directly
            data_dict = row["data"]
        else:
            # Skip invalid data
            continue
        
        # Create a new row with unpacked data
        new_row = {
            "username": row["username"],
            "field": row["field"],
            "date": row["date"],
            "process_name": row["process_name"],
            "role": row["role"],
            **data_dict  # Unpack all KPI fields
        }
        
        processed_results.append(new_row)
    
    return processed_results

# Function to save simulation data
def save_simulation_data(simulation_data):
    # Convert the data to a format suitable for PostgreSQL
    username = simulation_data.pop("username")
    field = simulation_data.pop("field")
    date = simulation_data.pop("date")
    simulation_type = simulation_data.pop("simulation_type", "Unknown")
    
    # Serialize the remaining data as JSON
    data_json = json.dumps(simulation_data)
    
    query = """
    INSERT INTO simulations (username, field, date, simulation_type, data)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (username, field, date, simulation_type, data_json)
    
    return execute_update(query, params)

# Function to get simulation data for a user
def get_user_simulation_data(username):
    query = """
    SELECT username, field, date, simulation_type, data
    FROM simulations
    WHERE username = %s
    ORDER BY date DESC
    """
    params = (username,)
    results = execute_query(query, params)
    
    if not results:
        return []
    
    # Process the results to unpack the JSON data
    processed_results = []
    for row in results:
        # Handle JSON data based on its type
        if isinstance(row["data"], str):
            # If it's a string, parse it
            data_dict = json.loads(row["data"])
        elif isinstance(row["data"], dict):
            # If it's already a dict, use it directly
            data_dict = row["data"]
        else:
            # Skip invalid data
            continue
        
        # Create a new row with unpacked data
        new_row = {
            "username": row["username"],
            "field": row["field"],
            "date": row["date"],
            "simulation_type": row["simulation_type"],
            **data_dict  # Unpack all simulation fields
        }
        
        processed_results.append(new_row)
    
    return processed_results

# Function to save user KPI preferences
def save_user_kpi_preferences(username, preferences):
    # First check if preferences already exist
    query_check = """
    SELECT username FROM user_kpi_preferences
    WHERE username = %s
    """
    result = execute_query(query_check, (username,))
    
    # Convert preferences to JSON
    preferences_json = json.dumps(preferences)
    
    if result:
        # Update existing preferences
        query = """
        UPDATE user_kpi_preferences
        SET preferences = %s, updated_at = %s
        WHERE username = %s
        """
        params = (preferences_json, datetime.now(), username)
    else:
        # Insert new preferences
        query = """
        INSERT INTO user_kpi_preferences (username, preferences, created_at, updated_at)
        VALUES (%s, %s, %s, %s)
        """
        params = (username, preferences_json, datetime.now(), datetime.now())
    
    return execute_update(query, params)

# Function to get user KPI preferences
def get_user_kpi_preferences(username):
    query = """
    SELECT preferences FROM user_kpi_preferences
    WHERE username = %s
    """
    
    result = execute_query(query, (username,))
    
    if result and len(result) > 0:
        # Handle JSON data based on its type
        preferences = result[0]["preferences"]
        if isinstance(preferences, str):
            return json.loads(preferences)
        elif isinstance(preferences, dict):
            return preferences
        else:
            return None
    else:
        return None
        
# Function to save extended KPI data
def save_extended_kpi_data(kpi_entry):
    # Extract data from the entry
    username = kpi_entry["username"]
    field = kpi_entry["field"]
    date = kpi_entry["date"]
    process_name = kpi_entry["process_name"]
    kpi_type = kpi_entry["kpi_type"]
    kpi_data = kpi_entry["kpi_data"]
    
    # Serialize the KPI data as JSON
    kpi_data_json = json.dumps(kpi_data)
    
    query = """
    INSERT INTO extended_kpi_data (username, field, date, process_name, kpi_type, kpi_data)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (username, field, date, process_name, kpi_type, kpi_data_json)
    
    return execute_update(query, params)

# Function to get extended KPI data for a user
def get_user_extended_kpi_data(username):
    query = """
    SELECT username, field, date, process_name, kpi_type, kpi_data
    FROM extended_kpi_data
    WHERE username = %s
    ORDER BY date
    """
    params = (username,)
    results = execute_query(query, params)
    
    if not results:
        return []
    
    # Process the results to unpack the JSON data
    processed_results = []
    for row in results:
        # Handle JSON data based on its type
        if isinstance(row["kpi_data"], str):
            # If it's a string, parse it
            kpi_data = json.loads(row["kpi_data"])
        elif isinstance(row["kpi_data"], dict):
            # If it's already a dict, use it directly
            kpi_data = row["kpi_data"]
        else:
            # Skip invalid data
            continue
        
        # Create a new row with unpacked data
        new_row = {
            "username": row["username"],
            "field": row["field"],
            "date": row["date"],
            "process_name": row["process_name"],
            "kpi_type": row["kpi_type"],
            "kpi_data": kpi_data
        }
        
        processed_results.append(new_row)
    
    return processed_results


def get_user_kpi_data_by_type(username, kpi_type):
    query = """
    SELECT username, field, date, process_name, kpi_type, kpi_data
    FROM extended_kpi_data
    WHERE username = %s AND kpi_type = %s
    ORDER BY date DESC
    """
    params = (username, kpi_type)
    results = execute_query(query, params)
    
    if not results:
        return []
    
    processed_results = []
    for row in results:
        if isinstance(row["kpi_data"], str):
            kpi_data = json.loads(row["kpi_data"])
        elif isinstance(row["kpi_data"], dict):
            kpi_data = row["kpi_data"]
        else:
            continue
            
        processed_results.append({
            "username": row["username"],
            "field": row["field"],
            "date": row["date"],
            "process_name": row["process_name"],
            "kpi_type": row["kpi_type"],
            **kpi_data
        })
    
    return processed_results

# Function to log user activity
def log_user_activity(username, activity_type, details=None):
    query = """
    INSERT INTO activity_logs (username, activity_type, details, timestamp)
    VALUES (%s, %s, %s, %s)
    """
    params = (username, activity_type, details, datetime.now())
    
    return execute_update(query, params)

# Function to get system logs
def get_system_logs(start_date=None, end_date=None):
    query_base = """
    SELECT id, username, activity_type, details, timestamp
    FROM activity_logs
    """
    
    if start_date and end_date:
        query = query_base + " WHERE timestamp BETWEEN %s AND %s ORDER BY timestamp DESC"
        params = (start_date, end_date)
    elif start_date:
        query = query_base + " WHERE timestamp >= %s ORDER BY timestamp DESC"
        params = (start_date,)
    elif end_date:
        query = query_base + " WHERE timestamp <= %s ORDER BY timestamp DESC"
        params = (end_date,)
    else:
        query = query_base + " ORDER BY timestamp DESC"
        params = None
    
    return execute_query(query, params)