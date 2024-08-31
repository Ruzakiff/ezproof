import asyncio
import logging
from email_processor import process_email
from gmail_service import get_gmail_service, check_for_new_emails

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def monitor_emails():
    logging.info("Starting OAuth flow...")
    service = await get_gmail_service()
    logging.info("OAuth flow completed. Successfully logged in.")
    logging.info("Starting email monitoring...")
    
    while True:
        new_emails = await check_for_new_emails(service)
        tasks = []
        for email_data in new_emails:
            task = asyncio.create_task(process_email(service, email_data))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks)
        
        await asyncio.sleep(60)  # Check every minute

if __name__ == "__main__":
    asyncio.run(monitor_emails())

