import os
from flask import Blueprint, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests

google_auth_bp = Blueprint('google_auth', __name__)

# Configure client IDs here or load them from environment variables
GOOGLE_CLIENT_IDS = [
    os.environ.get('GOOGLE_CLIENT_ID_WEB', ''),
    os.environ.get('GOOGLE_CLIENT_ID_ANDROID', ''),
    os.environ.get('GOOGLE_CLIENT_ID_IOS', '')
]

# Clean up empty strings
GOOGLE_CLIENT_IDS = [cid for cid in GOOGLE_CLIENT_IDS if cid]

@google_auth_bp.route('/auth/google', methods=['POST'])
def google_login():
    """Verify Google ID token sent from the client and return user details."""
    data = request.get_json()
    if not data or 'id_token' not in data:
        return jsonify({'error': 'Missing id_token in request body.'}), 400

    token = data['id_token']

    try:
        # Verify the ID token
        # If GOOGLE_CLIENT_IDS is empty, it verifies the token signature without checking the audience (useful for testing/development)
        idinfo = None
        if GOOGLE_CLIENT_IDS:
            # Try to verify with client IDs
            for client_id in GOOGLE_CLIENT_IDS:
                try:
                    idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
                    break
                except ValueError:
                    continue
            if idinfo is None:
                return jsonify({'error': 'Token verification failed: Invalid Client ID audience.'}), 401
        else:
            # Fallback: verify token signature and expiry without audience checking
            idinfo = id_token.verify_oauth2_token(token, requests.Request())

        # Token is valid, get user info
        user_data = {
            'uid': idinfo.get('sub'),
            'email': idinfo.get('email'),
            'email_verified': idinfo.get('email_verified'),
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture'),
            'given_name': idinfo.get('given_name'),
            'family_name': idinfo.get('family_name'),
            'locale': idinfo.get('locale')
        }

        return jsonify({
            'status': 'success',
            'message': 'Successfully authenticated with Google.',
            'user': user_data
        }), 200

    except ValueError as e:
        return jsonify({'error': f'Invalid token: {str(e)}'}), 401
    except Exception as e:
        return jsonify({'error': f'Authentication failed: {str(e)}'}), 500
