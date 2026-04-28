import os
import django
import sys

# Set up Django environment
sys.path.append('/home/workspace/service/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from config.firebase_config import send_push_notification

def test_notification():
    # Find a user with an FCM token (or create a dummy one)
    user = User.objects.filter(fcm_token__isnull=False).first()
    if not user:
        print("No user with FCM token found. Please register/login in the browser first.")
        return

    print(f"Testing notification for user: {user.username} (Token: {user.fcm_token[:20]}...)")
    
    response = send_push_notification(
        token=user.fcm_token,
        title="Test Notification",
        body="This is a test notification from the backend script.",
        data={"type": "test", "request_id": "123"}
    )
    
    if response:
        print(f"Success! Response: {response}")
    else:
        print("Failed to send notification. Check logs for errors.")

if __name__ == "__main__":
    test_notification()
