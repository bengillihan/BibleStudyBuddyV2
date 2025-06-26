# Use this Flask blueprint for Google authentication. Do not use flask-dance.

import json
import os

import requests
from app import db
from flask import Blueprint, redirect, request, url_for
from flask_login import login_required, login_user, logout_user
from models import User
from oauthlib.oauth2 import WebApplicationClient

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "temp_client_id")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "temp_client_secret")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Get the domain for OAuth redirects
dev_domain = os.environ.get("REPLIT_DEV_DOMAIN", "localhost")
production_domain = "biblestudybuddyv2-production.up.railway.app"

DEV_REDIRECT_URL = f'https://{dev_domain}/google_login/callback'
PROD_REDIRECT_URL = f'https://{production_domain}/google_login/callback'

# ALWAYS display setup instructions to the user:
print(f"""To make Google authentication work:
1. Go to https://console.cloud.google.com/apis/credentials
2. Create a new OAuth 2.0 Client ID
3. Add BOTH of these URLs to Authorized redirect URIs:
   - Development: {DEV_REDIRECT_URL}
   - Production: {PROD_REDIRECT_URL}

For detailed instructions, see:
https://docs.replit.com/additional-resources/google-auth-in-flask#set-up-your-oauth-app--client
""")

client = WebApplicationClient(GOOGLE_CLIENT_ID)

google_auth = Blueprint("google_auth", __name__)


def get_redirect_url():
    """Get the appropriate redirect URL based on the current domain"""
    host = request.host
    if "railway.app" in host:
        return PROD_REDIRECT_URL
    elif "replit.dev" in host:
        return DEV_REDIRECT_URL
    else:
        # Fallback for local development
        return request.base_url.replace("http://", "https://") + "/callback"

@google_auth.route("/google_login")
def login():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    redirect_url = get_redirect_url()
    
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_url,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@google_auth.route("/google_login/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    redirect_url = get_redirect_url()
    
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url.replace("http://", "https://"),
        redirect_url=redirect_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    userinfo = userinfo_response.json()
    if userinfo.get("email_verified"):
        users_email = userinfo["email"]
        users_name = userinfo["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User.query.filter_by(email=users_email).first()
    if not user:
        user = User(username=users_name, email=users_email)
        db.session.add(user)
        db.session.commit()

    login_user(user)

    return redirect(url_for("dashboard"))


@google_auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
