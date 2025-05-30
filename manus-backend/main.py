import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from api import health, chat, message
from fastapi.responses import JSONResponse
from core.file_monitor import FileMonitor
from core.file_processor import FileProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
MONITOR_FOLDER = os.getenv("DATA_ROOM_PATH")
RECURSIVE_MONITORING = True
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}

# Global services
file_monitor: FileMonitor = None
file_processor: FileProcessor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global file_monitor, file_processor
    try:
        file_processor = FileProcessor()
        file_monitor = FileMonitor(
            monitor_folder=MONITOR_FOLDER,
            allowed_extensions=ALLOWED_EXTENSIONS,
            recursive=RECURSIVE_MONITORING
        )
        file_monitor.set_file_processor(file_processor.process_file_event)
        success = await file_monitor.start()
        if success:
            logger.info("Application startup complete - file monitoring active")
        else:
            logger.error("Application startup failed - file monitoring not active")

    except Exception as e:
        logger.error(f"Error during application startup: {e}")

    yield

    logger.info("Shutting down application...")

    try:
        if file_monitor:
            await file_monitor.stop()
            logger.info("File monitoring stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

    logger.info("Application shutdown complete")

app = FastAPI(
    title="Manus Clone",
    version="0.0.1",
    lifespan=lifespan
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url)
        }
    )

# Routes goes here
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/chats", tags=["Chats"])
app.include_router(message.router, prefix="/messages", tags=["Messages"])




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )