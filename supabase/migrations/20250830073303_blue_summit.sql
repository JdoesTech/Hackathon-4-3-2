-- Scholarship Matchmaker Database Schema
-- Run this SQL script to set up your MySQL database

CREATE DATABASE IF NOT EXISTS scholarship_db;
USE scholarship_db;

-- Users table for authentication and profile data
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INT,
    country VARCHAR(100),
    education_level VARCHAR(50),
    gpa DECIMAL(3,2),
    field_of_study VARCHAR(255),
    financial_need VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Scholarships table with AI embeddings
CREATE TABLE IF NOT EXISTS scholarships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    amount INT,
    deadline DATE,
    country VARCHAR(100),
    min_gpa DECIMAL(3,2),
    education_level VARCHAR(50),
    field_of_study TEXT,
    financial_criteria VARCHAR(50),
    apply_url VARCHAR(500),
    embedding TEXT, -- JSON-encoded embedding vector
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Feedback table for user interactions
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    scholarship_id INT,
    rating TINYINT, -- 1 for like, 0 for dislike
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (scholarship_id) REFERENCES scholarships(id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_scholarships_country ON scholarships(country);
CREATE INDEX idx_scholarships_education_level ON scholarships(education_level);
CREATE INDEX idx_scholarships_min_gpa ON scholarships(min_gpa);
CREATE INDEX idx_feedback_user_scholarship ON feedback(user_id, scholarship_id);

-- Sample scholarship data (will be inserted by the application)
-- The application will automatically populate this table with sample data
-- including pre-computed embeddings for AI matching