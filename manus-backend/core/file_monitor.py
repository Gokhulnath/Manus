import asyncio
import logging
from pathlib import Path
from typing import Set, Callable, Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class FileMonitor:
    """File system monitoring service with async queue processing"""

    def __init__(
            self,
            monitor_folder: str,
            allowed_extensions: Set[str] = None,
            recursive: bool = True,
            file_processor: Optional[Callable] = None
    ):
        self.monitor_folder = Path(monitor_folder)
        self.allowed_extensions = allowed_extensions or {'.pdf', '.docx', '.txt'}
        self.recursive = recursive
        self.file_processor = file_processor

        # Internal state
        self.observer: Optional[Observer] = None
        self.processing_task: Optional[asyncio.Task] = None
        self.file_queue: Optional[asyncio.Queue] = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.is_running = False

    async def start(self):
        """Start the file monitoring service"""
        if self.is_running:
            logger.warning("File monitor is already running")
            return False

        try:
            # Validate monitor folder
            if not self.monitor_folder.exists():
                logger.error(f"Monitor folder does not exist: {self.monitor_folder}")
                return False

            # Store event loop reference
            self.event_loop = asyncio.get_running_loop()

            # Initialize queue
            self.file_queue = asyncio.Queue()

            # Start background processor
            self.processing_task = asyncio.create_task(self._process_file_queue())

            # Process all existing files first
            await self._process_existing_files()

            # Start file system monitoring
            event_handler = FileEventHandler(
                event_loop=self.event_loop,
                file_queue=self.file_queue,
                allowed_extensions=self.allowed_extensions
            )

            self.observer = Observer()
            self.observer.schedule(
                event_handler,
                str(self.monitor_folder),
                recursive=self.recursive
            )
            self.observer.start()

            self.is_running = True
            logger.info(f"File monitor started for: {self.monitor_folder}")
            logger.info(f"Recursive monitoring: {self.recursive}")
            logger.info(f"Allowed extensions: {self.allowed_extensions}")

            return True

        except Exception as e:
            logger.error(f"Failed to start file monitor: {e}")
            await self.stop()
            return False

    async def stop(self):
        """Stop the file monitoring service"""
        if not self.is_running:
            return

        logger.info("Stopping file monitor...")

        # Stop file system observer
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

        # Cancel processing task
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            self.processing_task = None

        self.is_running = False
        logger.info("File monitor stopped")

    def set_file_processor(self, processor: Callable):
        """Set or update the file processor function"""
        self.file_processor = processor

    async def _process_file_queue(self):
        """Background task to process files from the queue"""
        logger.info("File queue processor started")

        while True:
            try:
                # Wait for a file event
                event_type, file_path = await self.file_queue.get()

                # Process the file event
                await self._handle_file_event(event_type, file_path)

                # Mark task as done
                self.file_queue.task_done()

            except asyncio.CancelledError:
                logger.info("File queue processor cancelled")
                break
            except Exception as e:
                logger.error(f"Error in file queue processor: {e}")
                await asyncio.sleep(1)

    async def _handle_file_event(self, event_type: str, file_path: str):
        """Handle different types of file events"""
        try:
            logger.info(f"Handling {event_type} event for: {file_path}")

            if self.file_processor:
                # Call the registered file processor
                result = await self.file_processor(event_type, file_path)
                if result:
                    logger.info(f"Successfully processed {event_type} event for: {file_path}")
                else:
                    logger.warning(f"Failed to process {event_type} event for: {file_path}")
            else:
                logger.warning("No file processor registered")

        except Exception as e:
            logger.error(f"Error handling {event_type} event for {file_path}: {e}")

    async def _process_existing_files(self):
        """Process all existing files in the monitored folder"""
        logger.info("Scanning for existing files to process...")

        try:
            existing_files = []

            # Collect all files that match our criteria
            if self.recursive:
                # Use rglob for recursive search
                for ext in self.allowed_extensions:
                    pattern = f"**/*{ext}"
                    existing_files.extend(self.monitor_folder.rglob(pattern))
            else:
                # Use glob for non-recursive search
                for ext in self.allowed_extensions:
                    pattern = f"*{ext}"
                    existing_files.extend(self.monitor_folder.glob(pattern))

            # Remove duplicates and sort for consistent processing order
            existing_files = sorted(set(existing_files))

            if not existing_files:
                logger.info("No existing files found to process")
                return

            logger.info(f"Found {len(existing_files)} existing files to process")

            # Process each file
            processed_count = 0
            failed_count = 0

            for file_path in existing_files:
                try:
                    # Queue the file for processing as 'startup' event
                    await self.file_queue.put(('startup', str(file_path)))
                    processed_count += 1

                    # Add small delay to prevent overwhelming the system
                    if processed_count % 10 == 0:
                        await asyncio.sleep(0.1)

                except Exception as e:
                    logger.error(f"Error queuing existing file {file_path}: {e}")
                    failed_count += 1

            logger.info(f"Queued {processed_count} existing files for processing")
            if failed_count > 0:
                logger.warning(f"Failed to queue {failed_count} files")

            # Wait for all existing files to be processed before starting monitoring
            logger.info("Waiting for existing files to be processed...")
            await self.file_queue.join()
            logger.info("All existing files have been processed")

        except Exception as e:
            logger.error(f"Error processing existing files: {e}")
            raise


class FileEventHandler(FileSystemEventHandler):
    """Handle file system events and queue them for processing"""

    def __init__(self, event_loop: asyncio.AbstractEventLoop, file_queue: asyncio.Queue, allowed_extensions: Set[str]):
        self.event_loop = event_loop
        self.file_queue = file_queue
        self.allowed_extensions = allowed_extensions

    def _should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed based on extension"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.allowed_extensions

    def _queue_file_event(self, event_type: str, file_path: str):
        """Queue a file event for processing"""
        if self._should_process_file(file_path):
            logger.debug(f"Queuing {event_type} event for: {file_path}")
            asyncio.run_coroutine_threadsafe(
                self.file_queue.put((event_type, file_path)),
                self.event_loop
            )

    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"File created: {event.src_path}")
            self._queue_file_event('created', event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"File modified: {event.src_path}")
            self._queue_file_event('modified', event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")
            self._queue_file_event('deleted', event.src_path)