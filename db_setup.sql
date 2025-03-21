
-- Database setup for PostgreSQL

-- Create users table for authentication and user management
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    field VARCHAR(50) NOT NULL,
    role VARCHAR(10) DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    status VARCHAR(10) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create KPI data table
CREATE TABLE IF NOT EXISTS kpi_data (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    field VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    process_name VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

-- Create simulations table
CREATE TABLE IF NOT EXISTS simulations (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    field VARCHAR(50) NOT NULL,
    date TIMESTAMP NOT NULL,
    simulation_type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

-- Create activity logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

-- Insert admin user (password: 12345678)
INSERT INTO users (username, email, password, field, role, status)
SELECT 'zoubir', 'admin@example.com', encode(sha256('12345678'::bytea), 'hex'), 'Oil and Gas', 'admin', 'approved'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'zoubir');

-- Create user KPI preferences table
CREATE TABLE IF NOT EXISTS user_kpi_preferences (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    preferences JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

-- Create extended KPI data table for additional KPIs
CREATE TABLE IF NOT EXISTS extended_kpi_data (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    field VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    process_name VARCHAR(100) NOT NULL,
    kpi_type VARCHAR(50) NOT NULL,
    kpi_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_kpi_data_username ON kpi_data(username);
CREATE INDEX IF NOT EXISTS idx_kpi_data_date ON kpi_data(date);
CREATE INDEX IF NOT EXISTS idx_simulations_username ON simulations(username);
CREATE INDEX IF NOT EXISTS idx_activity_logs_username ON activity_logs(username);
CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp ON activity_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_user_kpi_preferences_username ON user_kpi_preferences(username);
CREATE INDEX IF NOT EXISTS idx_extended_kpi_data_username ON extended_kpi_data(username);
CREATE INDEX IF NOT EXISTS idx_extended_kpi_data_type ON extended_kpi_data(kpi_type);
