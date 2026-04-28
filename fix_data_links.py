import os
import django
import sys

# Set up Django environment
sys.path.append('/home/workspace/service/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from dispatch.models import ServiceRequest, Mechanic

def fix_data_links():
    print("Linking existing Mechanics to Users...")
    linked_users = set(Mechanic.objects.filter(user__isnull=False).values_list('user_id', flat=True))
    
    for mech in Mechanic.objects.filter(user__isnull=True):
        user = User.objects.filter(role=User.MECHANIC, username__icontains=mech.name).first()
        if user and user.id not in linked_users:
            try:
                mech.user = user
                mech.save()
                linked_users.add(user.id)
                print(f"Linked Mechanic '{mech.name}' to User '{user.username}'")
            except Exception as e:
                print(f"Error linking Mechanic '{mech.name}': {e}")
        else:
            print(f"Skipping or could not find unique user for Mechanic '{mech.name}'")

    print("\nLinking existing ServiceRequests to Users...")
    for req in ServiceRequest.objects.filter(customer__isnull=True):
        user = User.objects.filter(role=User.CUSTOMER, username=req.customer_name).first()
        if user:
            try:
                req.customer = user
                req.save()
                print(f"Linked Request #{req.id} ({req.customer_name}) to User '{user.username}'")
            except Exception as e:
                print(f"Error linking Request #{req.id}: {e}")
        else:
            print(f"Could not find user for Request #{req.id} (Name: {req.customer_name})")

if __name__ == "__main__":
    fix_data_links()
