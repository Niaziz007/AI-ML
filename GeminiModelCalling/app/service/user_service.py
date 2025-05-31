from fastapi import APIRouter, Request, File, UploadFile, HTTPException
from API.app.core.logger import logger
from API.app.core.config import get_db_connection
from API.app.LLM.Gemini import GCSGeminiHandler
import os
from pathlib import Path
import shutil
import base64
# Folder to save files
UPLOAD_FOLDER = Path('API/File')
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)  # Ensure the folder exists

def handleFile(file):
    """
    Handles the upload and saving of a file.
    """
    logger.info(f"File {file.filename} uploaded.")
    allowed_extensions = {"pdf", "jpg", "jpeg", "png", "gif"}
    
    try:
        # Validate file extension
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            logger.error("Invalid file type.")
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF, JPG, JPEG, PNG, GIF are allowed."
            )

        # Define the path to save the file
        file_path = UPLOAD_FOLDER / file.filename

        # Save the file to the specified path
        with file_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        logger.info(f"File {file.filename} saved to {file_path}")
        return str(file_path)

    except HTTPException as e:
        # Already raised with a meaningful message
        logger.error(f"HTTPException while handling file: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Error saving the file.")


def handleFilebase64Data(base64_data, output_filename="output_image.png"):
    """
    Handles decoding base64 data and saving it as an image.
    """
    logger.info(f"Base64 data received. {base64_data}")
    try:
        # Decode the base64 data
        image_data = base64.b64decode(base64_data)

        # Define the output file path
        file_path = UPLOAD_FOLDER / output_filename

        # Write the image data to a file
        with file_path.open("wb") as img_file:
            img_file.write(image_data)

        logger.info(f"Base64 data saved as {file_path}")
        return str(file_path)

    except base64.binascii.Error as e:
        logger.error(f"Invalid base64 data: {e}")
        raise HTTPException(
            status_code=400, detail="Invalid base64 data. Please check the input."
        )
    except Exception as e:
        logger.error(f"Unexpected error processing base64 data: {e}")
        raise HTTPException(status_code=500, detail="Error processing base64 data.")