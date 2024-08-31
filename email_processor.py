import asyncio
import random
import logging
import os
from gmail_service import get_attachment_type, get_attachment_data, send_reply_email, mark_email_as_read
from autoediting.backremove import remove_background_from_data
from config import load_processing_config
from anal import run_checks, print_image_info

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_email(service, email_data):
    sender, subject, message_id, content, attachments = email_data
    config = load_processing_config()
    
    logger.info(f"Processing email with subject: {subject}")
    logger.info(f"Number of attachments: {len(attachments)}")
    
    processing_results = []
    for attachment in attachments:
        attachment_type = get_attachment_type(attachment)
        logger.info(f"Attachment type: {attachment_type}")
        if attachment_type in config:
            result = await process_attachment(service, attachment, content, message_id, config[attachment_type])
            processing_results.append(result)
        else:
            logger.warning(f"No processor found for attachment type: {attachment_type}")
    
    reply_content, attachment_data = generate_reply(content, processing_results)
    
    await send_reply_email(service, sender, subject, reply_content, message_id, attachment_data)
    await mark_email_as_read(service, message_id)

async def process_attachment(service, attachment, email_content, message_id, processor_name):
    logger.info(f"Processing attachment with processor: {processor_name}")
    if processor_name == 'process_image':
        return await process_image(service, attachment, email_content, message_id)
    # Add more processors here if needed in the future
    logger.warning(f"Unknown processor: {processor_name}")
    return None

async def process_image(service, attachment, email_content, message_id):
    logger.info(f"Processing image: {attachment['filename']}")
    image_data = await get_attachment_data(service, 'me', message_id, attachment['id'])
    if image_data:
        base_filename = f"email_{message_id}_{attachment['filename']}"
        try:
            # Run image analysis
            print_dpi = 300  # You might want to make this configurable
            desired_width_inch = 8.5  # You might want to make this configurable
            desired_height_inch = 11  # You might want to make this configurable
            bleed_inch = 0.125  # You might want to make this configurable

            analysis_results, halftone_image = run_checks(image_data, print_dpi, desired_width_inch, desired_height_inch, bleed_inch)
            
            # Get detailed image info
            image_info = {}
            print_image_info(image_data, image_info)

            # Process the image (background removal)
            results = await asyncio.to_thread(remove_background_from_data, image_data, base_filename)
            
            if results:
                processed_images = []
                for result in results:
                    for alpha_type in ['without_alpha', 'with_alpha']:
                        processed_images.append({
                            'model': result['model'],
                            'alpha': alpha_type == 'with_alpha',
                            'filename': result[alpha_type]['filename'],
                            'path': result[alpha_type]['path']
                        })
                
                logger.info(f"Successfully processed image: {attachment['filename']}")
                return {
                    'filename': attachment['filename'],
                    'status': 'success',
                    'processed_images': processed_images,
                    'analysis': analysis_results,
                    'image_info': image_info
                }
            else:
                logger.warning(f"No results from background removal for: {attachment['filename']}")
        except Exception as e:
            logger.error(f"Error processing image {attachment['filename']}: {str(e)}")
    else:
        logger.error(f"Failed to get attachment data for: {attachment['filename']}")
    
    return {
        'filename': attachment['filename'],
        'status': 'failed',
        'processed_images': None,
        'analysis': None,
        'image_info': None
    }

def generate_reply(original_content, processing_results):
    reply = "Thank you for your email. We've processed and analyzed your attachments:\n\n"
    attachment_data = None
    u2netp_alpha_image = None

    for result in processing_results:
        if result is not None:
            reply += f"- {result['filename']}:\n"
            reply += f"  Processing status: {result['status']}\n"
            
            if result['status'] == 'success':
                if result['analysis']:
                    reply += "  Image Analysis:\n"
                    for check, analysis_result in result['analysis'].items():
                        reply += f"    {check.capitalize()}: {analysis_result}\n"
                
                if result['image_info']:
                    reply += "  Image Information:\n"
                    for key, value in result['image_info'].items():
                        reply += f"    {key}: {value}\n"
                
                if result['processed_images']:
                    reply += "  Processed images:\n"
                    for img in result['processed_images']:
                        reply += f"    - {img['model']} ({'with' if img['alpha'] else 'without'} alpha matting)\n"
                        if img['model'] == 'u2netp' and img['alpha']:
                            u2netp_alpha_image = img
            else:
                reply += "  The attachment could not be processed or analyzed.\n"
        else:
            reply += "- An attachment could not be processed\n"
    
    if not processing_results:
        reply += "No attachments were processed.\n"
    
    if u2netp_alpha_image:
        reply += "\nWe've attached the processed image using u2netp model with alpha matting for your reference."
        with open(u2netp_alpha_image['path'], 'rb') as f:
            image_data = f.read()
        attachment_data = {
            'filename': u2netp_alpha_image['filename'],
            'data': image_data
        }
    else:
        reply += "\nUnfortunately, we couldn't process any of the attachments successfully with the u2netp model and alpha matting."

    reply += "\nIf you have any questions or need further assistance with printing, please don't hesitate to ask."

    return reply, attachment_data