import os
import sys
import json
import django

sys.path.append('/home/workspace/service/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.firebase_config import initialize_firebase, send_push_notification
import firebase_admin

# Simulate Vercel Env Var
with open('/home/workspace/service/backend/.env', 'r') as f:
    for line in f:
        if line.startswith('FIREBASE_SERVICE_ACCOUNT_JSON='):
            env_val = line.split('=', 1)[1].strip()
            os.environ['FIREBASE_SERVICE_ACCOUNT_JSON'] = env_val

# Remove file to force fallback
if os.path.exists('/home/workspace/service/backend/firebase-service-account.json'):
    os.rename('/home/workspace/service/backend/firebase-service-account.json', '/home/workspace/service/backend/firebase-service-account.json.bak')

try:
    initialize_firebase()
    print("Apps:", firebase_admin._apps)
finally:
    if os.path.exists('/home/workspace/service/backend/firebase-service-account.json.bak'):
        os.rename('/home/workspace/service/backend/firebase-service-account.json.bak', '/home/workspace/service/backend/firebase-service-account.json')
