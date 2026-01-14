import datetime
import functools

import bcrypt
import jwt
from flask import jsonify, request

SECRET_KEY = "DEV"  # os.urandom(24)


def hash_password(password):
    """Hash a password using bcrypt"""
    ## Convert password to bytes if it's a string
    if isinstance(password, str):
        password = password.encode('utf-8')

    ## Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)

    return hashed


def check_password(password, hashed):
    """Verify a password against its hash"""
    ## Convert password to bytes if it's a string
    if isinstance(password, str):
        password = password.encode('utf-8')

    ## Check if the password matches the hash
    return bcrypt.checkpw(password, hashed)


def generate_token(username, role):
    """Generate a JWT token for the authenticated user"""
    ## Token expires after 30 minutes
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)

    payload = {
        'username': username,
        'role': role,
        'exp': expiration
    }

    ## Create the JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    """Verify the JWT token"""
    try:
        ## Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        ## Token has expired
        return None
    except jwt.InvalidTokenError:
        ## Invalid token
        return None


def token_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"status": "error", "message": "Missing or invalid token"}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)

        if payload:
            return view(**kwargs)
        else:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 401

    return wrapped_view
