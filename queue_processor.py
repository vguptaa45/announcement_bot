# import asyncio
# import logging
# from supabase import create_client
# from datetime import datetime
# from config import *

# class QueueProcessor:
#     def __init__(self, queue):
#         self.queue = queue
#         self.supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
#         self.last_processed = {}  # Store last processed timestamp for each stock

#     async def process_queue(self):
#         while True:
#             try:
#                 # Non-blocking get with timeout
#                 try:
#                     stock_data = self.queue.get_nowait()
#                 except:
#                     await asyncio.sleep(0.1)
#                     continue

#                 stock_name = stock_data["stock_name"]
#                 current_timestamp = stock_data["timestamp"]
                
#                 # Check if we've processed this stock recently (within last 2 seconds)
#                 if stock_name in self.last_processed:
#                     last_time = datetime.fromisoformat(self.last_processed[stock_name])
#                     current_time = datetime.fromisoformat(current_timestamp)
#                     time_diff = (current_time - last_time).total_seconds()
#                     if time_diff < 2:
#                         logging.info(f"Skipping {stock_name} - processed {time_diff:.1f} seconds ago")
#                         continue

#                 logging.info(f"Processing stock: {stock_name}")

#                 # Update the last processed timestamp
#                 self.last_processed[stock_name] = current_timestamp

#                 response = self.supabase.table("stocks_wishlist") \
#                     .select("user_list") \
#                     .eq("company_id", stock_name) \
#                     .execute()

#                 if response.data:
#                     users = response.data[0].get("user_list", [])
#                     if users:
#                         logging.info(f"Found users for {stock_name}: {users}")
#                         await self.notify_users(stock_name, users)

#             except Exception as e:
#                 logging.error(f"Error processing queue: {e}")
#                 await asyncio.sleep(1)

#     async def notify_users(self, stock_name, users):
#         logging.info(f"Notifying users {users} about update in stock {stock_name}")
#         # Add your notification logic here



import asyncio
import logging
from supabase import create_client
from datetime import datetime
from config import *
from pdf_extractor import download_pdf_from_name
from summary_generator import generate_summary
from message_sender import AnnouncementMessageSender

class QueueProcessor:
    def __init__(self, queue):
        self.queue = queue
        self.supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        self.last_processed = {}  # Store last processed timestamp for each stock
        self.message_sender = AnnouncementMessageSender()

    async def process_queue(self):
        while True:
            try:
                # Non-blocking get with timeout
                try:
                    stock_data = self.queue.get_nowait()
                except:
                    await asyncio.sleep(0.1)
                    continue

                stock_name = stock_data["stock_name"]
                current_timestamp = stock_data["timestamp"]
                
                # Check if we've processed this stock recently (within last 2 seconds)
                if stock_name in self.last_processed:
                    last_time = datetime.fromisoformat(self.last_processed[stock_name])
                    current_time = datetime.fromisoformat(current_timestamp)
                    time_diff = (current_time - last_time).total_seconds()
                    if time_diff < 2:
                        logging.info(f"Skipping {stock_name} - processed {time_diff:.1f} seconds ago")
                        continue

                logging.info(f"Processing stock: {stock_name}")

                # Update the last processed timestamp
                self.last_processed[stock_name] = current_timestamp

                response = self.supabase.table("stocks_wishlist") \
                    .select("user_list") \
                    .eq("company_id", stock_name) \
                    .execute()

                if response.data:
                    users = response.data[0].get("user_list", [])
                    if users:
                        logging.info(f"Found users for {stock_name}: {users}")
                        
                        # Extract text from PDF
                        pdf_text = download_pdf_from_name(stock_data["pdf_name"])
                        
                        if pdf_text:
                            # Generate summary
                            summary = generate_summary(pdf_text)
                            
                            if summary:
                                # Prepare announcement data
                                announcement = {
                                    "stock_name": stock_name,
                                    "title": stock_data["title"],
                                    "pdf_name": stock_data["pdf_name"],
                                    "summary": summary
                                }
                                
                                # Send message to users
                                try:
                                    self.message_sender.send_announcement(announcement, users)
                                    logging.info(f"Successfully sent announcement for {stock_name}")
                                except Exception as e:
                                    logging.error(f"Error sending announcement: {e}")
                            else:
                                logging.error(f"Failed to generate summary for {stock_name}")
                        else:
                            logging.error(f"Failed to extract PDF text for {stock_name}")

            except Exception as e:
                logging.error(f"Error processing queue: {e}")
                await asyncio.sleep(1)

    async def notify_users(self, stock_name, users):
        logging.info(f"Notifying users {users} about update in stock {stock_name}")
        # This method is now handled by message_sender
