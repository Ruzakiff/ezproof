from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64

async def send_reply_email(service, recipient, subject, body, thread_id, attachment_data=None):
    message = MIMEMultipart()
    message['to'] = recipient
    message['subject'] = f"Re: {subject}"
    message.attach(MIMEText(body))

    if attachment_data:
        image = MIMEImage(attachment_data['data'], _subtype="png")
        image.add_header('Content-Disposition', 'attachment', filename=attachment_data['filename'])
        message.attach(image)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        message = service.users().messages().send(
            userId="me",
            body={
                'raw': raw_message,
                'threadId': thread_id
            }
        ).execute()
        print(f"Message Id: {message['id']}")
        return message
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

async def mark_email_as_read(service, message_id):
    try:
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
    except Exception as error:
        print(f"An error occurred: {error}")
