import imaplib
import base64
import time
import json
import os
import re
import email
from email import policy
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes required for inserting messages and reading metadata
SCOPES = ['https://www.googleapis.com/auth/gmail.insert', 
          'https://www.googleapis.com/auth/gmail.labels',
          'https://www.googleapis.com/auth/gmail.readonly']

def load_config():
    """Loads ACCOUNTS from environment variable."""
    accounts_json = os.environ.get('ACCOUNTS_JSON')
    if not accounts_json:
        raise ValueError("Environment variable ACCOUNTS_JSON is not set.")
    try:
        return json.loads(accounts_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse ACCOUNTS_JSON: {str(e)}")

def get_gmail_service():
    """Authenticates and returns the Gmail API service instance from env vars."""
    token_json_str = os.environ.get('GMAIL_TOKEN_JSON')
    if not token_json_str:
        raise ValueError("Environment variable GMAIL_TOKEN_JSON is not set.")
    
    try:
        token_info = json.loads(token_json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse GMAIL_TOKEN_JSON: {str(e)}")

    creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            print("[*] Access token expired, refreshing...")
            creds.refresh(Request())
            # Note: In a stateless CI environment, we cannot easily save the new 
            # access token back to GitHub Secrets. However, the refresh_token 
            # remains valid for future runs, so this in-memory refresh is sufficient.
        else:
            raise Exception("Credentials are invalid and cannot be refreshed.")
            
    return build('gmail', 'v1', credentials=creds)

def extract_message_ids(header_value):
    """Extracts raw Message-IDs from email headers, removing < and >."""
    if not header_value:
        return []
    # Find all strings between < and >
    return re.findall(r'<([^>]+)>', str(header_value))

def find_thread_id_in_gmail(service, raw_email_bytes):
    """
    Parses the email to find 'In-Reply-To' or 'References',
    searches Gmail for those IDs, and returns the existing threadId if found.
    """
    try:
        msg = email.message_from_bytes(raw_email_bytes, policy=policy.default)
        
        reply_to_ids = extract_message_ids(msg.get('In-Reply-To', ''))
        reference_ids = extract_message_ids(msg.get('References', ''))
        
        # Prioritize In-Reply-To, then check References (reverse order to get latest parent first)
        search_ids = reply_to_ids + list(reversed(reference_ids))
        
        for msg_id in search_ids:
            # Gmail search operator for exact RFC822 Message-ID
            query = f'rfc822msgid:{msg_id}'
            response = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
            
            if 'messages' in response and len(response['messages']) > 0:
                found_thread_id = response['messages'][0]['threadId']
                print(f"[*] Found existing Thread ID: {found_thread_id} via Message-ID: {msg_id}")
                return found_thread_id
                
        return None
    except Exception as e:
        print(f"[-] Error while searching for thread ID: {str(e)}")
        return None

def insert_message_to_gmail(service, raw_email_bytes):
    """Inserts a raw RFC822 email into Gmail inbox, maintaining threads."""
    try:
        # Step 1: Try to find an existing thread ID based on email headers
        thread_id = find_thread_id_in_gmail(service, raw_email_bytes)
        
        # Step 2: Prepare the insert payload
        encoded_message = base64.urlsafe_b64encode(raw_email_bytes).decode('ascii')
        body = {
            'raw': encoded_message,
            'labelIds': ['INBOX', 'UNREAD']
        }
        
        # Step 3: Attach threadId if we found one
        if thread_id:
            body['threadId'] = thread_id
            
        message = service.users().messages().insert(userId='me', body=body).execute()
        print(f"[+] Successfully inserted message to Gmail. Msg ID: {message['id']}, Thread ID: {message.get('threadId', 'N/A')}")
        return True
    except HttpError as error:
        print(f"[-] An error occurred during Gmail injection: {error}")
        return False

def process_imap_account(account_config, gmail_service):
    """Connects to IMAP, fetches unseen emails, and pushes them to Gmail."""
    print(f"\n--- Processing account: {account_config.get('name', 'Unknown')} ---")
    mail = None
    try:
        mail = imaplib.IMAP4_SSL(account_config['imap_server'], account_config['imap_port'])
        mail.login(account_config['email'], account_config['password'])
        mail.select('INBOX')

        status, response = mail.search(None, 'UNSEEN')
        if status != 'OK':
            print("[-] Failed to search emails.")
            return

        email_ids = response[0].split()
        print(f"[*] Found {len(email_ids)} new email(s).")

        for e_id in email_ids:
            # Fetch the raw email (RFC822)
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            if status != 'OK':
                print(f"[-] Failed to fetch email ID {e_id.decode('ascii')}.")
                continue

            # msg_data[0][1] contains the raw bytes of the email
            raw_email_bytes = msg_data[0][1]
            
            # Inject to Gmail
            success = insert_message_to_gmail(gmail_service, raw_email_bytes)
            
            if success:
                # Mark as seen on the source server to prevent duplicate fetching
                mail.store(e_id, '+FLAGS', '\\Seen')
                print(f"[*] Marked email ID {e_id.decode('ascii')} as Seen on source server.")
            
            time.sleep(1)

    except Exception as e:
        print(f"[-] Exception occurred while processing {account_config.get('name', 'Unknown')}: {str(e)}")
    finally:
        if mail:
            try:
                mail.logout()
            except Exception:
                pass

def main():
    print("[*] Initializing Mail Bridge with Thread Support...")
    try:
        accounts = load_config()
        gmail_service = get_gmail_service()
    except Exception as e:
        print(f"[-] Initialization failed: {str(e)}")
        return

    for account in accounts:
        process_imap_account(account, gmail_service)
        
    print("\n[*] Mail Bridge execution completed.")

if __name__ == '__main__':
    main()