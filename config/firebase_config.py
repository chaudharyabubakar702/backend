import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import os
import json
import logging

logger = logging.getLogger(__name__)

# Path to the service account JSON file
SERVICE_ACCOUNT_PATH = os.path.join(settings.BASE_DIR, 'firebase-service-account.json')

def initialize_firebase():
    if not firebase_admin._apps:
        try:
            if os.path.exists(SERVICE_ACCOUNT_PATH):
                cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin initialized from JSON file.")
            else:
                # Fallback to environment variable if file not found (useful for CI/CD)
                cred_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
                if cred_json:
                    cred_dict = json.loads(cred_json)
                    # Vercel and other platforms sometimes escape newlines in env variables
                    if 'private_key' in cred_dict:
                        cred_dict['private_key'] = cred_dict['private_key'].replace('\\n', '\n')
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase Admin initialized from environment variable.")
                else:
                    logger.error("Firebase Service Account file NOT found at %s", SERVICE_ACCOUNT_PATH)
        except Exception as e:
            logger.error(f"Error initializing Firebase Admin: {e}")

def send_push_notification(token, title, body, data=None):
    initialize_firebase()
    if not firebase_admin._apps:
        logger.error("Cannot send notification: Firebase Admin not initialized.")
        return None
        
    payload_data = data or {}
    payload_data["title"] = title
    payload_data["body"] = body

    message = messaging.Message(
        data=payload_data,
        token=token,
    )
    try:
        response = messaging.send(message)
        logger.info(f"Successfully sent message: {response}")
        return response
    except Exception as e:
        logger.error(f"Error sending message to token {token[:10]}...: {e}")
        return None
