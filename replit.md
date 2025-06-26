# Bible Study Buddy

## Overview

This is a web-based Bible study application called "Bible Study Buddy" built with Flask that allows users to create, manage, and analyze their personal Bible study sessions. The application features Google OAuth authentication, study session management with reflection questions, and text analysis capabilities for scripture passages.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome 6.0
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Backend Architecture
- **Web Framework**: Flask 3.1.1
- **Database ORM**: SQLAlchemy 2.0.41 with Flask-SQLAlchemy
- **Authentication**: Flask-Login with Google OAuth 2.0
- **WSGI Server**: Gunicorn for production deployment
- **Text Processing**: NLTK for natural language processing

### Database Schema
- **Users Table**: Stores user authentication data (id, username, email)
- **Study Sessions Table**: Stores Bible study data including:
  - Basic info (passage, date, user_id)
  - 10 reflection questions (question_1 through question_10)
  - Full passage text and analysis results
  - Timestamps for creation and updates

## Key Components

### Authentication System
- **Google OAuth Integration**: Custom implementation using oauthlib (not flask-dance)
- **Session Management**: Flask-Login for user session handling
- **Security**: Environment-based secret key management

### Study Management
- **CRUD Operations**: Create, read, update studies
- **Text Analysis**: Word frequency and bigram analysis using NLTK
- **Data Persistence**: JSON storage for frequency analysis results
- **User Isolation**: All studies scoped to authenticated users

### Text Analysis Engine
- **Word Frequency**: Top 20 most common words (excluding stopwords)
- **Bigram Analysis**: Top 20 most common word pairs
- **Text Processing**: Tokenization, normalization, and stopword filtering

## Data Flow

1. **User Authentication**: Google OAuth → User creation/login → Session establishment
2. **Study Creation**: Form submission → Text analysis → Database storage
3. **Study Retrieval**: Database query → Template rendering → User display
4. **Study Updates**: Form submission → Re-analysis → Database update

## External Dependencies

### Authentication
- **Google OAuth 2.0**: Requires GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET
- **Redirect URI**: Configured for Replit environment with HTTPS enforcement

### Database
- **PostgreSQL**: Primary database (configured via DATABASE_URL environment variable)
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability

### Text Processing
- **NLTK Data**: Automatic download of punkt tokenizer and stopwords corpus
- **Language Support**: English stopwords and tokenization

## Deployment Strategy

### Environment Configuration
- **Replit Deployment**: Configured for autoscale deployment target
- **Environment Variables**: 
  - SESSION_SECRET for Flask sessions
  - DATABASE_URL for PostgreSQL connection
  - Google OAuth credentials

### Server Configuration
- **Gunicorn**: Production WSGI server with port binding and reload capability
- **Proxy Handling**: ProxyFix middleware for proper header handling
- **Port Configuration**: Default port 5000 with environment override

### Development Workflow
- **Hot Reload**: Gunicorn configured with --reload for development
- **Debug Mode**: Flask debug mode enabled in development
- **Database Initialization**: Automatic model import and table creation

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- June 26, 2025: Initial setup with Flask, Google OAuth, and Supabase integration
- June 26, 2025: Updated app name to "Bible Study Buddy"
- June 26, 2025: Configured Google OAuth for dual environment support (dev + Railway production)
- June 26, 2025: Created PostgreSQL database in Replit and imported 15 historical Bible studies for Ben Gillihan
- June 26, 2025: Fixed template error causing 500 error on production (removed undefined moment() function)
- June 26, 2025: Updated study form with question labels above inputs, Bible Gateway ESV links, and text analysis preview