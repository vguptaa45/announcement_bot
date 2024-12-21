import asyncio
import websockets
import json
import logging
from datetime import datetime
from multiprocessing import Queue
from config import *

logging.basicConfig(level=logging.INFO)

class AnnouncementListener:
    def __init__(self, queue):
        self.queue = queue

    async def subscribe_to_changes(self):
        while True:
            try:
                async with websockets.connect(WS_URL) as websocket:
                    logging.info("Connected to Supabase Realtime")

                    join_message = {
                        "topic": f"realtime:public:{TABLE_NAME}",
                        "event": "phx_join",
                        "payload": {},
                        "ref": "1"
                    }
                    await websocket.send(json.dumps(join_message))
                    response = await websocket.recv()
                    logging.info(f"Join response: {response}")

                    heartbeat_task = asyncio.create_task(self.send_heartbeat(websocket))

                    try:
                        while True:
                            message = await websocket.recv()
                            await self.handle_message(message)
                    except websockets.exceptions.ConnectionClosed:
                        logging.info("Connection closed, attempting to reconnect...")
                    finally:
                        heartbeat_task.cancel()

            except Exception as e:
                logging.error(f"Error: {e}")
                logging.info("Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    async def send_heartbeat(self, websocket):
        while True:
            try:
                heartbeat_message = {
                    "topic": "phoenix",
                    "event": "heartbeat",
                    "payload": {},
                    "ref": "3"
                }
                await websocket.send(json.dumps(heartbeat_message))
                await asyncio.sleep(30)
            except websockets.exceptions.ConnectionClosed:
                break

    async def handle_message(self, message):
        data = json.loads(message)
        if data.get("event") == "UPDATE" or data.get("event") == "INSERT":
            stock_name = data.get("payload", {}).get("record", {}).get("stock_name")
            title = data.get("payload", {}).get("record", {}).get("title")
            pdf_name = data.get("payload", {}).get("record", {}).get("content")
            if stock_name:
                logging.info(f"Adding stock to queue: {stock_name}")
                stock_data = {
                    "stock_name": stock_name,
                    "title": title,
                    "pdf_name": pdf_name,
                    "timestamp": datetime.now().isoformat()
                }
                self.queue.put(stock_data)
