#!/usr/bin/env python3
"""
Comprehensive test script for signup and login flows
"""
import requests
import time
import re

def test_signup_and_login():
    base_url = "http://127.0.0.1:8000"
    
    # Use a session to maintain cookies
    session = requests.Session()
    
    print("=" * 60)
    print("🧪 TESTING SIGNUP AND LOGIN FLOWS")
    print("=" * 60)
    
    # Step 1: Test signup page load
    print("\n1️⃣ Testing signup page load...")
    signup_url = f"{base_url}/student/signup/"
    response = session.get(signup_url)
    print(f"   GET {signup_url} → Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ Signup page failed to load: {response.status_code}")
        return
    
    # Extract CSRF token
    csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    if not csrf_match:
        print("   ❌ No CSRF token found")
        return
    
    csrf_token = csrf_match.group(1)
    print(f"   ✅ CSRF token found: {csrf_token[:20]}...")
    
    # Step 2: Test signup submission
    print("\n2️⃣ Testing signup submission...")
    unique_id = f"test{int(time.time())}"
    signup_data = {
        'csrfmiddlewaretoken': csrf_token,
        'firstname': 'Test User',
        'emailID': f'{unique_id}@test.com',
        'mobile': '1234567890',
        'address': 'Test Address',
        'studentID': unique_id,
        'college': 'Test College',
        'password': 'testpass123',
        'confirmPassword': 'testpass123',
        'terms': 'on'
    }
    
    response = session.post(signup_url, data=signup_data, allow_redirects=False)
    print(f"   POST {signup_url} → Status: {response.status_code}")
    
    if response.status_code == 302:
        redirect_location = response.headers.get('Location', 'No Location')
        print(f"   ✅ Redirect to: {redirect_location}")
        
        # Follow redirect
        if redirect_location.startswith('/'):
            full_redirect = base_url + redirect_location
        else:
            full_redirect = redirect_location
            
        redirect_response = session.get(full_redirect)
        print(f"   GET {full_redirect} → Status: {redirect_response.status_code}")
        
        if "Account created successfully" in redirect_response.text:
            print("   ✅ Success message found on login page!")
        else:
            print("   ❌ Success message not found")
            
    else:
        print(f"   ❌ Expected redirect (302), got {response.status_code}")
        print(f"   Response preview: {response.text[:200]}...")
        return
    
    # Step 3: Test login page load
    print("\n3️⃣ Testing login page load...")
    login_url = f"{base_url}/student/login/"
    response = session.get(login_url)
    print(f"   GET {login_url} → Status: {response.status_code}")
    
    # Extract new CSRF token for login
    csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print(f"   ✅ CSRF token found: {csrf_token[:20]}...")
    else:
        print("   ❌ No CSRF token found for login")
        return
    
    # Step 4: Test login submission
    print("\n4️⃣ Testing login submission...")
    login_data = {
        'csrfmiddlewaretoken': csrf_token,
        'studentID': unique_id,
        'password': 'testpass123'
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"   POST {login_url} → Status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        redirect_location = response.headers.get('Location', 'No Location')
        print(f"   ✅ Login redirect to: {redirect_location}")
        
        # Check for session cookie
        cookies = dict(response.cookies)
        if 'sessionid' in cookies:
            print(f"   ✅ Session cookie set: {cookies['sessionid'][:20]}...")
        else:
            print("   ❌ No session cookie set")
        
        # Follow redirect to dashboard
        if redirect_location.startswith('/'):
            full_redirect = base_url + redirect_location
        else:
            full_redirect = redirect_location
            
        dashboard_response = session.get(full_redirect)
        print(f"   GET {full_redirect} → Status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            if "My Dashboard" in dashboard_response.text:
                print("   ✅ Successfully reached dashboard!")
            elif "Welcome back" in dashboard_response.text:
                print("   ✅ Successfully logged in and saw welcome message!")
            else:
                print("   ❌ Reached page but no dashboard/welcome content found")
        else:
            print(f"   ❌ Dashboard page returned {dashboard_response.status_code}")
            
    else:
        print(f"   ❌ Expected redirect (302), got {response.status_code}")
        if response.status_code == 200:
            if "Invalid credentials" in response.text:
                print("   ❌ Login failed - invalid credentials")
            else:
                print("   ❌ Login form re-displayed (check credentials)")
        print(f"   Response preview: {response.text[:300]}...")
    
    print("\n" + "=" * 60)
    print("🏁 TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_signup_and_login()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to http://127.0.0.1:8000")
        print("💡 Make sure Django server is running:")
        print("   cd C:\\Users\\milin\\PycharmProjects\\LibrarySystem\\library")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")