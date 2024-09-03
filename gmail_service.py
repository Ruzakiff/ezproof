import logging  # Add this import at the top of the file

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase  # Add this line
import email.encoders as encoders  # Add this line if not already present

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Add this line near the top of the file, after the imports
logger = logging.getLogger(__name__)

async def get_gmail_service():
    creds = None
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
            content = get_email_content(msg)
            attachments = get_attachments(msg)
            new_emails.append((sender, subject, message['id'], content, attachments))
        
        return new_emails
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def get_email_content(msg):
    parts = msg['payload'].get('parts', [])
    content = ""
    for part in parts:
        if part['mimeType'] == 'text/plain':
            data = part['body'].get('data')
            if data:
                content += base64.urlsafe_b64decode(data).decode('utf-8')
    return content

def get_attachments(msg):
    attachments = []
    parts = msg['payload'].get('parts', [])
    for part in parts:
        if part.get('filename'):
            attachment = {
                'id': part['body']['attachmentId'],
                'filename': part['filename'],
                'mimeType': part['mimeType']
            }
            attachments.append(attachment)
    return attachments

def get_attachment_type(attachment):
    return attachment['mimeType']

async def get_attachment_data(service, user_id, message_id, attachment_id):
    try:
        attachment = service.users().messages().attachments().get(
            userId=user_id, messageId=message_id, id=attachment_id).execute()
        data = attachment['data']
        return base64.urlsafe_b64decode(data)
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

async def send_reply_email(service, to, subject, body, thread_id, attachments_data):
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = f"Re: {subject}"
    message.attach(MIMEText(body))

    for attachment in attachments_data:
        filename = attachment['filename']
        content = attachment['data']
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(content)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        message.attach(part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        sent_message = service.users().messages().send(userId='me', body={'raw': raw_message, 'threadId': thread_id}).execute()
        logger.info(f"Message sent. Message ID: {sent_message['id']}")
    except Exception as e:
        logger.error(f"An error occurred while sending the email: {e}")

async def mark_email_as_read(service, message_id):
    try:
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
    except Exception as error:
        print(f"An error occurred: {error}")


