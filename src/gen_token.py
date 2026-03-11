import os
from google_auth_oauthlib.flow import InstalledAppFlow

# The updated scopes requiring Read-Only access for searching Thread IDs
SCOPES = [
    'https://www.googleapis.com/auth/gmail.insert', 
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def generate_new_token():
    # 1. Delete old token if exists to force re-consent
    if os.path.exists('token.json'):
        print("[*] Removing old token.json to force permission update...")
        os.remove('token.json')
        
    if not os.path.exists('credentials.json'):
        print("[-] Error: credentials.json not found in the current directory.")
        return

    print("[*] Starting OAuth flow. Please check your browser...")
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    
    # This will open your web browser
    creds = flow.run_local_server(port=0)
    
    # Save the new token
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
        
    print("[+] Success! A new token.json has been generated.")
    print("[+] Please copy the ENTIRE content of token.json and update your GitHub Secret: GMAIL_TOKEN_JSON")

if __name__ == '__main__':
    generate_new_token()