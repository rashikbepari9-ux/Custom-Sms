from http.server import BaseHTTPRequestHandler
import json
import requests
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Get parameters
        sms = query_params.get('sms', [''])[0]
        number = query_params.get('number', [''])[0]
        owner = query_params.get('owner', ['@RASHIK_69'])[0]
        business = query_params.get('business', ['Credit - @RASHIK_69'])[0]
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Validate inputs
        if not sms or not number:
            response = {
                "success": False,
                "owner": owner,
                "reason": "Missing required fields: sms and number"
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
            return
        
        # Clean phone number
        number = ''.join(filter(lambda x: x.isdigit() or x == '+', number))
        
        # Carrybee API URL
        url = "https://api-merchant.carrybee.com/api/v2/merchant/register"
        
        # Request Headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
            "Origin": "https://merchant.carrybee.com",
            "Referer": "https://merchant.carrybee.com/"
        }
        
        # Request Payload
        payload = {
            "name": sms,
            "phone_number": number,
            "business_name": business
        }
        
        try:
            # Send registration request
            api_response = requests.post(url, headers=headers, json=payload)
            
            # Accept both 200 and 201 status codes
            if api_response.status_code in [200, 201]:
                result = api_response.json()
                
                if not result.get("error"):
                    otp_data = result.get('data', {})
                    otp_prefix = otp_data.get('otp_prefix', '')
                    
                    # SMS Message Format
                    sms_message = f"[Carrybee] Hi {sms}, your code is {otp_prefix} to join by-{owner}"
                    
                    response = {
                        "success": False,
                        "owner": owner,
                        "reason": "Merchant registered successfully",
                        "sms_message": sms_message,
                        "otp_details": {
                            "otp_prefix": otp_prefix,
                            "otp_expires_at": otp_data.get('otp_expires_at', ''),
                            "full_message": sms_message,
                            "phone_number": otp_data.get('phone_number', number),
                            "business_name": otp_data.get('business_name', business)
                        },
                        "input": {
                            "name": sms,
                            "phone": number,
                            "business": business
                        }
                    }
                else:
                    response = {
                        "success": False,
                        "owner": owner,
                        "reason": result.get('message', 'Registration failed'),
                        "error_details": result.get('errors', {})
                    }
            else:
                response = {
                    "success": False,
                    "owner": owner,
                    "reason": f"API Error: HTTP {api_response.status_code}",
                    "details": api_response.text
                }
                
        except requests.exceptions.RequestException as e:
            response = {
                "success": False,
                "owner": owner,
                "reason": f"Network error: {str(e)}"
            }
        except Exception as e:
            response = {
                "success": False,
                "owner": owner,
                "reason": f"Unexpected error: {str(e)}"
            }
        
        # Return JSON response
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
