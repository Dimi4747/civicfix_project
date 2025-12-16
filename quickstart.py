#!/usr/bin/env python
"""
🚀 Quick Start Script for CivicFix
Initializes the project and prepares it for development/production
"""

import os
import sys
import subprocess
import django
from pathlib import Path

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def run_command(cmd, description):
    """Run shell command"""
    print(f"🔧 {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} - OK\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED: {e}\n")
        return False

def create_test_users():
    """Create test users"""
    print_header("Creating Test Users")
    
    users = [
        {
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'Test',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'email': 'moderator1@test.com',
            'first_name': 'Modérateur',
            'last_name': 'Un',
            'role': 'moderator',
        },
        {
            'email': 'moderator2@test.com',
            'first_name': 'Modérateur',
            'last_name': 'Deux',
            'role': 'moderator',
        },
    ]
    
    for user_data in users:
        email = user_data['email']
        
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                email=email,
                password='TestPassword123!',
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                is_staff=user_data.get('is_staff', False),
                is_superuser=user_data.get('is_superuser', False),
            )
            print(f"✅ Created: {email} ({user_data['role']})")
        else:
            print(f"⏭️  Skipped: {email} (already exists)")
    
    # Create regular users
    for i in range(1, 6):
        email = f'user{i}@test.com'
        
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                email=email,
                password='TestPassword123!',
                first_name=f'User',
                last_name=f'{i}',
                role='user',
            )
            print(f"✅ Created: {email} (user)")
        else:
            print(f"⏭️  Skipped: {email} (already exists)")
    
    print("\n📝 Login credentials:")
    print("   Email: admin@test.com")
    print("   Password: TestPassword123!")

def main():
    """Main initialization flow"""
    print_header("🎯 CivicFix - Quick Start Setup")
    
    # Step 1: Check dependencies
    print_header("Step 1: Checking Dependencies")
    try:
        import django
        import rest_framework
        import channels
        import tailwind
        print("✅ All dependencies installed\n")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt\n")
        return

    # Step 2: Run migrations
    print_header("Step 2: Running Database Migrations")
    try:
        call_command('migrate', verbosity=1)
        print("✅ Migrations applied successfully\n")
    except Exception as e:
        print(f"❌ Migration failed: {e}\n")
        return

    # Step 3: Create test users
    create_test_users()

    # Step 4: Collect static files
    print_header("Step 3: Collecting Static Files")
    try:
        call_command('collectstatic', '--noinput', verbosity=0)
        print("✅ Static files collected\n")
    except Exception as e:
        print(f"⚠️  Static collection warning: {e}\n")

    # Step 5: Run checks
    print_header("Step 4: Running Django System Checks")
    try:
        call_command('check', verbosity=1)
        print("✅ System checks passed\n")
    except Exception as e:
        print(f"⚠️  Check warning: {e}\n")

    # Final summary
    print_header("✅ Setup Complete!")
    print("""
📋 NEXT STEPS:

1️⃣  Run the development server:
    python manage.py runserver

2️⃣  Access the application:
    • Homepage: http://127.0.0.1:8000/
    • Admin Panel: http://127.0.0.1:8000/admin/
    • Dashboard: http://127.0.0.1:8000/dashboard/

3️⃣  Login with test credentials:
    Email: admin@test.com
    Password: TestPassword123!

4️⃣  Create your first report:
    • Click "Nouveau Rapport" button
    • Fill in the form
    • Add attachments
    • Submit!

5️⃣  Explore features:
    • Notifications: /notifications/
    • My Reports: /reports/my-reports/
    • Dashboard: /dashboard/

📚 DOCUMENTATION:
    • PROJECT_COMPLETE.md - Full project overview
    • DEPLOY_SETUP.md - Deployment guide
    • API_DOCUMENTATION.md - API reference

🆘 TROUBLESHOOTING:
    • Port 8000 busy? python manage.py runserver 8001
    • Database error? python manage.py migrate --fake
    • Missing files? python manage.py collectstatic

💡 TIPS:
    • Use Django shell: python manage.py shell
    • Check logs: Check browser console for JS errors
    • Reset DB: python manage.py flush

Happy coding! 🚀
    """)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        sys.exit(1)
