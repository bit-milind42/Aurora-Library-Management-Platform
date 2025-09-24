#!/usr/bin/env python
"""
Quick test script to verify signup functionality
"""
import requests
import urllib.parse

# Test signup endpoint
url = "http://127.0.0.1:8000/student/signup/"

# First get the page to obtain CSRF token
session = requests.Session()
response = session.get(url)
print(f"GET /student/signup/ Status: {response.status_code}")

# Extract CSRF token from the response
csrf_token = None
if 'csrfmiddlewaretoken' in response.text:
    start = response.text.find('name="csrfmiddlewaretoken" value="') + len('name="csrfmiddlewaretoken" value="')
    end = response.text.find('"', start)
    csrf_token = response.text[start:end]
    print(f"CSRF Token found: {csrf_token[:20]}...")

# Test data
test_data = {
    'csrfmiddlewaretoken': csrf_token,
    'firstname': 'Test User',
    'emailID': 'test@example.com',
    'mobile': '1234567890',
    'address': 'Test Address',
    'studentID': 'testuser123',
    'college': 'Test College',
    'password': 'testpass123',
    'confirmPassword': 'testpass123',
    'terms': 'on'
}

# Submit form
print("\nSubmitting signup form...")
response = session.post(url, data=test_data, allow_redirects=False)
print(f"POST /student/signup/ Status: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")

# Check for redirect
if response.status_code == 302:
    redirect_location = response.headers.get('Location', 'No Location header')
    print(f"✅ Redirect detected to: {redirect_location}")
    
    # Follow the redirect
    if redirect_location:
        redirect_response = session.get(redirect_location)
        print(f"GET {redirect_location} Status: {redirect_response.status_code}")
        
        # Check for success message in the response
        if 'Account created successfully' in redirect_response.text:
            print("✅ Success message found on login page!")
        else:
            print("❌ Success message not found")
else:
    print(f"❌ No redirect detected. Response content preview:")
    print(response.text[:500])