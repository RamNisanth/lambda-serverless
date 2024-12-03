import json
import requests
import ssl
import socket
from datetime import datetime

def lambda_function(event, context):
    url = event.get('queryStringParameters', {}).get('URL', 'default_value')  # Use .get() to avoid KeyError if 'URL' is missing
    if not url:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'URL' in event"})
        }
    
    URL_RESPONSE = {}
    
    # Check if the website is reachable
    try:
        response = requests.get(url, timeout=10)  # Add timeout for better error handling
        if response.status_code == 200:
            print(f"Website is up: {url}")
            URL_RESPONSE['Status'] = "Uppp!!!!!"
        else:
            print(f"Website is down (HTTP {response.status_code}): {url}")
            URL_RESPONSE['Status'] = "Downnn"
    except requests.exceptions.RequestException as e:
        print(f"Error checking website: {e}")
        URL_RESPONSE['Status'] = "Error"
        URL_RESPONSE['ErrorMessage'] = str(e)
    
    # Check SSL certificate
    try:
        # Remove protocol from the URL to get the hostname
        host = url.replace("https://", "").replace("http://", "").split('/')[0]
        port = 443
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host) as connection:
            connection.settimeout(5)  # Set a timeout for the connection
            connection.connect((host, port))
            
            # Get certificate details
            ssl_info = connection.getpeercert()
            expiry_date = ssl_info['notAfter']
            
            # Convert expiry date to datetime
            ssl_expiry_date = datetime.strptime(expiry_date, "%b %d %H:%M:%S %Y GMT")
            
            # Output the expiry date
            print(f"SSL certificate for {url} expires on {ssl_expiry_date}")
            if ssl_expiry_date < datetime.now():
                print(f"WARNING: SSL certificate for {url} has expired!")
                URL_RESPONSE['Expiry'] = "Expired"
                URL_RESPONSE['ExpiryDate'] = ssl_expiry_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                print(f"SSL certificate for {url} is valid.")
                URL_RESPONSE['Expiry'] = "Not_Expired!!!"
                URL_RESPONSE['ExpiryDate'] = ssl_expiry_date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error checking SSL certificate: {e}")
        URL_RESPONSE['SSL_Status'] = "Error"
        URL_RESPONSE['ErrorMessage'] = str(e)
    
    # Return the response
    Return_response = {"statusCode": 200, "body": json.dumps(URL_RESPONSE)}
    return Return_response
