# Bible Study Buddy

A Flask web application for creating, managing, and analyzing personal Bible study sessions. Sign in with Google, record your passage and reflection notes, and get word frequency analysis of the scripture you study.

## Features

- Google OAuth sign-in
- Create and edit study sessions with a Bible passage, date, and up to 10 reflection questions
- Word frequency and bigram (phrase) analysis of passage text using NLTK
- Auto-saving drafts to prevent data loss
- Responsive dark-themed UI (Bootstrap 5)

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask 3 |
| Database ORM | SQLAlchemy 2 / Flask-SQLAlchemy |
| Auth | Google OAuth 2.0 via oauthlib, Flask-Login |
| Text analysis | NLTK (punkt tokenizer, stopwords, Porter stemmer) |
| Production server | Gunicorn |
| Database | PostgreSQL |
| Deployment | Railway |

## Local Development

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- A PostgreSQL database (or set `DATABASE_URL` to a local Postgres connection)
- A Google OAuth 2.0 Client ID/Secret ([create one here](https://console.cloud.google.com/apis/credentials))

### Setup

```bash
# Install dependencies
uv sync

# Copy and fill in environment variables
cp .env.example .env

# Run the development server
python main.py
```

The app will be available at `http://localhost:5000`.

### Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SESSION_SECRET` | Random secret key for Flask sessions |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth client secret |

### Google OAuth Setup

In the [Google Cloud Console](https://console.cloud.google.com/apis/credentials), add your callback URL as an authorized redirect URI:

```
https://<your-domain>/google_login/callback
```

The app dynamically constructs the callback URL from the incoming request host, so any domain works without code changes.

## Deployment (Railway)

The app is configured to deploy automatically on Railway:

- **Build:** `pip install .`
- **Start:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 60 --preload main:app`

Set the four environment variables above in your Railway service settings. The database tables are created automatically on first startup.

## Project Structure

```
├── app.py              # Flask app factory, DB and login manager setup
├── main.py             # Entry point (dev server)
├── models.py           # SQLAlchemy models (User, StudySession)
├── routes.py           # All page and API routes
├── google_auth.py      # Google OAuth blueprint
├── text_analysis.py    # NLTK word/bigram frequency analysis
├── templates/          # Jinja2 HTML templates
├── static/             # Favicon assets
├── pyproject.toml      # Dependencies
├── railway.yaml        # Railway deployment config
└── Procfile            # Gunicorn start command
```
