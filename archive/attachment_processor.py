import asyncio
from autoediting.backremove import remove_background_from_data
from gmail_service import get_attachment_type, get_attachment_data

async def process_attachment(service, attachment, email_content, message_id):
    attachment_type = get_attachment_type(attachment)
    if attachment_type.startswith('image/'):
        return await process_image(service, attachment, email_content, message_id)
    # Add more attachment type processors as needed
    return None

async def process_image(service, attachment, email_content, message_id):
    keywords = extract_keywords(email_content)
    image_data = await get_attachment_data(service, 'me', message_id, attachment['id'])
    if image_data:
        processed_images = await asyncio.to_thread(remove_background_from_data, image_data, 'h')
        return {
            'filename': attachment['filename'],
            'status': 'success' if processed_images else 'failed',
            'processed_images': processed_images
        }
    else:
        return {
            'filename': attachment['filename'],
            'status': 'failed',
            'processed_images': None
        }

def extract_keywords(email_content):
    return email_content

# Remove the get_attachment_type function from here