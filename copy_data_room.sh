#!/bin/bash

# Define source and target destinations
SOURCE_DIR="./Data Room"
BACKEND_DEST="manus-backend/data-room"
FRONTEND_DEST="manus-frontend/public/data-room"

# Check source exists
if [ ! -d "$SOURCE_DIR" ]; then
  echo "Source folder '$SOURCE_DIR' does not exist."
  exit 1
fi

# Copy to backend
if [ -d "manus-backend" ]; then
  echo "🗑️ Removing existing '$BACKEND_DEST'..."
  rm -rf "$BACKEND_DEST"

  echo "📁 Copying to '$BACKEND_DEST'..."
  cp -R "$SOURCE_DIR" "$BACKEND_DEST"
else
  echo "'manus-backend' directory not found."
fi

# Copy to frontend
if [ -d "manus-frontend/public" ]; then
  echo "🗑️ Removing existing '$FRONTEND_DEST'..."
  rm -rf "$FRONTEND_DEST"

  echo "📁 Copying to '$FRONTEND_DEST'..."
  cp -R "$SOURCE_DIR" "$FRONTEND_DEST"
else
  echo "❌ 'manus-frontend/public' directory not found."
fi

echo "Done."
