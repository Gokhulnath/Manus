import logging
from pathlib import Path
from agent.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class FileProcessor:
    def __init__(self):
        self.document_processor = DocumentProcessor()

    async def process_file_event(self, event_type: str, file_path: str) -> bool:
        """Process different types of file events"""
        try:
            if event_type == 'deleted':
                return await self._handle_file_deletion(file_path)
            elif event_type in ['created', 'modified', 'startup']:
                return await self._post_process_content(file_path, event_type)
            else:
                logger.warning(f"Unknown event type: {event_type}")
                return False

        except Exception as e:
            logger.error(f"Error processing {event_type} event for {file_path}: {e}")
            return False

    async def _handle_file_deletion(self, file_path: str) -> bool:
        """Handle file deletion events"""
        try:
            logger.info(f"Processing file deletion: {file_path}")

            deletion_record = {
                'file_path': file_path,
                'deleted_at': Path(file_path).stat().st_mtime if Path(file_path).exists() else None,
                'event_type': 'deletion'
            }

            logger.info(f"Deletion record created: {deletion_record}")

            await self.document_processor.delete_document(file_path=file_path)

            logger.info(f"Successfully handled deletion of: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error handling file deletion {file_path}: {e}")
            return False

    async def _post_process_content(self, file_path: str, event_type: str) -> bool:
        """Perform processing on file"""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.warning(f"File no longer exists: {file_path}")
                return False

            logger.info(f"Processing {event_type} file: {file_path}")

            if event_type == 'startup' or event_type == 'created':
                await self.document_processor.process_document(file_path)
            elif event_type == 'modified':
                # todo
                pass

            logger.info(f"Successfully processed {event_type} file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error in post-processing for {file_path}: {e}")
            return False