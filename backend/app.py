from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'scholarship_db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 5432))
}

# Initialize sentence transformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to supabase: {e}")
        return None

def init_database():
    """Initialize database tables"""
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        # Create users table
        cursor.execute("""
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create scholarships table
        cursor.execute("""
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
                embedding TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                scholarship_id INT,
                rating TINYINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (scholarship_id) REFERENCES scholarships(id)
            )
        """)
        
        connection.commit()
        
        # Insert sample scholarships if table is empty
        cursor.execute("SELECT COUNT(*) FROM scholarships")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_scholarships = [
                {
                    'name': 'Global Excellence Scholarship',
                    'description': 'Supporting outstanding students pursuing STEM fields with focus on innovation and research',
                    'amount': 15000,
                    'deadline': '2025-06-15',
                    'country': 'Global',
                    'min_gpa': 3.5,
                    'education_level': 'Undergraduate',
                    'field_of_study': 'Computer Science, Engineering, Mathematics, Physics',
                    'financial_criteria': 'High',
                    'apply_url': 'https://example.com/apply/global-excellence'
                },
                {
                    'name': 'Innovation Leaders Award',
                    'description': 'For creative students in technology and business who demonstrate leadership potential',
                    'amount': 10000,
                    'deadline': '2025-05-30',
                    'country': 'USA',
                    'min_gpa': 3.0,
                    'education_level': 'Graduate',
                    'field_of_study': 'Business, Technology, Innovation, Entrepreneurship',
                    'financial_criteria': 'Medium',
                    'apply_url': 'https://example.com/apply/innovation-leaders'
                },
                {
                    'name': 'Future Scientists Grant',
                    'description': 'Encouraging the next generation of researchers in life sciences and medical fields',
                    'amount': 8000,
                    'deadline': '2025-07-10',
                    'country': 'Global',
                    'min_gpa': 3.2,
                    'education_level': 'Both',
                    'field_of_study': 'Biology, Chemistry, Physics, Medicine, Biotechnology',
                    'financial_criteria': 'High',
                    'apply_url': 'https://example.com/apply/future-scientists'
                },
                {
                    'name': 'Creative Arts Fellowship',
                    'description': 'Supporting artistic and creative endeavors in visual arts, music, and creative writing',
                    'amount': 12000,
                    'deadline': '2025-04-20',
                    'country': 'Global',
                    'min_gpa': 2.8,
                    'education_level': 'Both',
                    'field_of_study': 'Art, Design, Creative Writing, Music, Film, Theater',
                    'financial_criteria': 'Medium',
                    'apply_url': 'https://example.com/apply/creative-arts'
                },
                {
                    'name': 'Social Impact Scholarship',
                    'description': 'For students working on social change projects and community development initiatives',
                    'amount': 7500,
                    'deadline': '2025-08-15',
                    'country': 'Global',
                    'min_gpa': 3.0,
                    'education_level': 'Both',
                    'field_of_study': 'Social Work, Psychology, Public Policy, Sociology, International Relations',
                    'financial_criteria': 'High',
                    'apply_url': 'https://example.com/apply/social-impact'
                },
                {
                    'name': 'International Student Aid',
                    'description': 'Supporting international students in higher education with focus on cultural exchange',
                    'amount': 9000,
                    'deadline': '2025-09-01',
                    'country': 'USA',
                    'min_gpa': 3.3,
                    'education_level': 'Both',
                    'field_of_study': 'Any field of study welcome',
                    'financial_criteria': 'High',
                    'apply_url': 'https://example.com/apply/international-aid'
                },
                {
                    'name': 'Tech Diversity Initiative',
                    'description': 'Promoting diversity in technology fields with mentorship and career support',
                    'amount': 11000,
                    'deadline': '2025-03-31',
                    'country': 'Global',
                    'min_gpa': 3.1,
                    'education_level': 'Both',
                    'field_of_study': 'Computer Science, Software Engineering, Data Science, Cybersecurity',
                    'financial_criteria': 'Medium',
                    'apply_url': 'https://example.com/apply/tech-diversity'
                },
                {
                    'name': 'Environmental Leadership Grant',
                    'description': 'For students passionate about environmental conservation and sustainable development',
                    'amount': 6500,
                    'deadline': '2025-10-15',
                    'country': 'Global',
                    'min_gpa': 2.9,
                    'education_level': 'Both',
                    'field_of_study': 'Environmental Science, Sustainability, Climate Studies, Green Technology',
                    'financial_criteria': 'High',
                    'apply_url': 'https://example.com/apply/environmental-leadership'
                }
            ]
            
            for scholarship in sample_scholarships:
                # Generate embedding for scholarship
                scholarship_text = f"{scholarship['description']} {scholarship['field_of_study']}"
                embedding = model.encode(scholarship_text)
                embedding_json = json.dumps(embedding.tolist())
                
                cursor.execute("""
                    INSERT INTO scholarships 
                    (name, description, amount, deadline, country, min_gpa, education_level, 
                     field_of_study, financial_criteria, apply_url, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    scholarship['name'],
                    scholarship['description'],
                    scholarship['amount'],
                    scholarship['deadline'],
                    scholarship['country'],
                    scholarship['min_gpa'],
                    scholarship['education_level'],
                    scholarship['field_of_study'],
                    scholarship['financial_criteria'],
                    scholarship['apply_url'],
                    embedding_json
                ))
            
            connection.commit()
        
        return True
        
    except Error as e:
        print(f"Error initializing database: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        name = data['name']
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO users (email, password, name) VALUES (%s, %s, %s)
        """, (email, hashed_password, name))
        
        connection.commit()
        user_id = cursor.lastrowid
        
        return jsonify({'success': True, 'userId': user_id})
        
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        session['user_id'] = user['id']
        return jsonify({'success': True, 'userId': user['id'], 'name': user['name']})
        
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    try:
        data = request.get_json()
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET age = %s, country = %s, education_level = %s, gpa = %s, 
                field_of_study = %s, financial_need = %s
            WHERE id = %s
        """, (
            data['age'],
            data['country'],
            data['education_level'],
            data['gpa'],
            data['field_of_study'],
            data['financial_need'],
            user_id
        ))
        
        connection.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': 'Profile update failed'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/matches/<int:user_id>', methods=['GET'])
def get_matches(user_id):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Get user profile
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get all scholarships
        cursor.execute("SELECT * FROM scholarships")
        scholarships = cursor.fetchall()
        
        # Rule-based filtering
        eligible_scholarships = []
        for scholarship in scholarships:
            # GPA check
            if user['gpa'] < scholarship['min_gpa']:
                continue
            
            # Country check
            if scholarship['country'] != 'Global' and scholarship['country'] != user['country']:
                continue
            
            # Education level check
            if (scholarship['education_level'] != 'Both' and 
                scholarship['education_level'] != user['education_level']):
                continue
            
            eligible_scholarships.append(scholarship)
        
        # Semantic similarity matching
        if eligible_scholarships:
            # Create user profile text
            user_profile_text = f"{user['field_of_study']} {user['financial_need']} {user['education_level']} student interested in academic excellence"
            user_embedding = model.encode([user_profile_text])
            
            # Calculate similarities
            ranked_scholarships = []
            for scholarship in eligible_scholarships:
                if scholarship['embedding']:
                    # Load scholarship embedding
                    scholarship_embedding = np.array(json.loads(scholarship['embedding'])).reshape(1, -1)
                    
                    # Calculate cosine similarity
                    similarity = cosine_similarity(user_embedding, scholarship_embedding)[0][0]
                    
                    # Add field matching bonus
                    field_bonus = 0
                    if scholarship['field_of_study']:
                        user_field_lower = user['field_of_study'].lower()
                        scholarship_fields_lower = scholarship['field_of_study'].lower()
                        if (user_field_lower in scholarship_fields_lower or 
                            any(field.strip().lower() in user_field_lower 
                                for field in scholarship['field_of_study'].split(','))):
                            field_bonus = 0.2
                    
                    # Add financial need bonus
                    financial_bonus = 0
                    if scholarship['financial_criteria'] == user['financial_need']:
                        financial_bonus = 0.1
                    
                    # Calculate final confidence score
                    confidence = min((similarity + field_bonus + financial_bonus) * 100, 100)
                    confidence = max(confidence, 30)  # Minimum confidence
                    
                    scholarship['confidence'] = int(confidence)
                    ranked_scholarships.append(scholarship)
            
            # Sort by confidence and return top 3
            ranked_scholarships.sort(key=lambda x: x['confidence'], reverse=True)
            top_matches = ranked_scholarships[:3]
            
            # Convert datetime objects to strings for JSON serialization
            for match in top_matches:
                if isinstance(match['deadline'], datetime):
                    match['deadline'] = match['deadline'].strftime('%Y-%m-%d')
                # Remove embedding from response
                match.pop('embedding', None)
            
            return jsonify(top_matches)
        
        return jsonify([])
        
    except Exception as e:
        print(f"Error in get_matches: {e}")
        return jsonify({'error': 'Matching failed'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO feedback (user_id, scholarship_id, rating) VALUES (%s, %s, %s)
        """, (data['userId'], data['scholarshipId'], data['rating']))
        
        connection.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': 'Feedback submission failed'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    if init_database():
        print("Database initialized successfully!")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to initialize database. Please check your MySQL connection.")