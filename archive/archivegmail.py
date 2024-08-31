import os.path
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

async def get_gmail_service():
    creds = None
    # Comment out or remove the following lines
    # if os.path.exists('token.json'):
    #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

async def check_for_new_emails(service):
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread has:attachment').execute()
        messages = results.get('messages', [])
        
        new_emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = msg['payload']['headers']
            subject = next(header['value'] for header in email_data if header['name'] == 'Subject')
            sender = next(header['value'] for header in email_data if header['name'] == 'From')
            new_emails.append((sender, subject, message['id']))
        
        return new_emails
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

async def process_email(service, sender, subject, message_id):
    # Simulate processing time
    await asyncio.sleep(5)
    
    try:
        message = MIMEText('Thank you for your email with the image attachment. We have processed it.')
        message['to'] = sender
        message['subject'] = f'Re: {subject}'
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        
        send_message = service.users().messages().send(userId='me', body=create_message).execute()
        print(f'Message Id: {send_message["id"]}')
        
        # Mark the original message as read
        service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')

async def monitor_emails():
    service = await get_gmail_service()
    
    while True:
        new_emails = await check_for_new_emails(service)
        tasks = []
        for sender, subject, message_id in new_emails:
            print(f"New email with image attachment from: {sender}")
            task = asyncio.create_task(process_email(service, sender, subject, message_id))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks)
        
        await asyncio.sleep(60)  # Check every minute

if __name__ == "__main__":
    asyncio.run(monitor_emails())

