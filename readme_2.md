# Scholarship Matchmaker

An AI-powered web application that helps students find their perfect scholarship matches using advanced semantic similarity algorithms and rule-based filtering.

## Features

- **Smart Authentication**: Secure user registration and login with password hashing
- **Comprehensive Profiling**: Detailed student profile collection (age, GPA, field of study, etc.)
- **AI-Powered Matching**: Uses Hugging Face sentence transformers for semantic similarity
- **Rule-Based Filtering**: Filters scholarships by eligibility criteria (GPA, country, education level)
- **Top 3 Recommendations**: Returns the best matches with confidence scores
- **Interactive Feedback**: Like/dislike system to improve future recommendations
- **Modern UI**: Colorful, responsive design with smooth animations
- **Real-time Validation**: Form validation with helpful error messages

## Quick Start

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)

### Installation

1. **Clone and setup the project**:
   ```bash
   git clone <your-repo>
   cd scholarship-matchmaker
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database**:
   ```bash
   # Create database and run schema
   mysql -u root -p < database.sql
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your MySQL credentials
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Open your browser** and navigate to `http://localhost:5000`

## Database Setup

The application uses MySQL with three main tables:

- **users**: Student profiles and authentication
- **scholarships**: Scholarship data with AI embeddings
- **feedback**: User feedback for recommendation improvement

Run the provided `database.sql` script to set up the schema automatically.

## AI Matching Algorithm

The scholarship matching system combines:

1. **Rule-based filtering**: Eliminates ineligible scholarships based on:
   - Minimum GPA requirements
   - Country restrictions
   - Education level requirements

2. **Semantic similarity**: Uses Hugging Face's `sentence-transformers/all-MiniLM-L6-v2` model to:
   - Generate embeddings for student profiles
   - Compare with pre-computed scholarship embeddings
   - Calculate cosine similarity scores

3. **Bonus scoring**: Additional points for:
   - Exact field of study matches
   - Financial need alignment

## UI Features

- **Glassmorphism design** with backdrop blur effects
- **Gradient animations** and smooth transitions
- **Responsive layout** for all device sizes
- **Interactive elements** with hover states and micro-interactions
- **Progress indicators** and loading animations
- **Visual confidence bars** for match scores

## Pages

1. **Authentication**: Login/register with tab switching
2. **Profile Setup**: Comprehensive form with validation
3. **Results**: Top 3 scholarship matches with apply buttons and feedback

## Configuration

Key configuration options in `config.py`:

- Database connection settings
- Hugging Face model selection
- Flask app configuration
- Security settings

##  Deployment

For production deployment:

1. Set up a production MySQL database
2. Configure environment variables for production
3. Set `FLASK_DEBUG=False`
4. Use a production WSGI server like Gunicorn
5. Set up SSL/HTTPS for security

## Contributing

This project is designed for hackathon use and rapid prototyping. Feel free to extend the matching algorithm, add more scholarship data, or enhance the UI!

## License

MIT License - feel free to use this for your hackathon projects!
