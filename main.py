import asyncio
import signal
import sys
from multiprocessing import Queue, Process
from announcement_listener import AnnouncementListener
from queue_processor import QueueProcessor
import logging


def run_listener(queue):
    listener = AnnouncementListener(queue)
    asyncio.run(listener.subscribe_to_changes())

def run_processor(queue):
    processor = QueueProcessor(queue)
    asyncio.run(processor.process_queue())

class StockNotificationSystem:
    def __init__(self):
        self.queue = Queue()
        self.processes = []

    def start(self):
        # Create processes for both components
        listener_process = Process(target=run_listener, args=(self.queue,))
        processor_process = Process(target=run_processor, args=(self.queue,))
        
        self.processes.extend([listener_process, processor_process])
        
        # Set up signal handlers for graceful shutdown
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self.handle_signal)
        
        # Start processes
        for process in self.processes:
            process.start()
        
        # Wait for processes to complete
        for process in self.processes:
            process.join()

    def handle_signal(self, signum, frame):
        logging.info(f"Received signal {signum}")
        self.cleanup()

    def cleanup(self):
        logging.info("Cleaning up resources...")
        for process in self.processes:
            process.terminate()
        sys.exit(0)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    system = StockNotificationSystem()
    
    try:
        system.start()
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt, shutting down...")
        system.cleanup()

if __name__ == "__main__":
    main()