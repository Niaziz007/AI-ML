from API.app.core.logger import logger
import os
import time
import re
import json
from PIL import Image
from google.cloud import storage
from PIL import Image, ImageFilter
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import warnings
import schedule
import time
import pandas as pd
import pymssql
import sqlalchemy as sa
import urllib
from datetime import datetime

from vertexai.generative_models import (
    GenerativeModel,
    HarmCategory,
    HarmBlockThreshold,
    Part,
    SafetySetting,
)

warnings.filterwarnings('ignore')

safety_config = [
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.BLOCK_NONE,  # No blocking for dangerous content
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=HarmBlockThreshold.BLOCK_NONE,  # No blocking for harassment
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=HarmBlockThreshold.BLOCK_NONE,  # No blocking for hate speech
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=HarmBlockThreshold.BLOCK_NONE,  # No blocking for sexually explicit content
    )
]

class GCSGeminiHandler:
    def __init__(
        self,
        project_id="aiml-365220", 
        location="us-central1",
        bucket_name="grounding_example",
        upload_folder="Cards"
    ):
        self.project_id = project_id
        self.location = location
        self.bucket_name = bucket_name
        self.upload_folder = upload_folder
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "API/app/aiml-365220-7d5d084cd436.json"
        vertexai.init(project=self.project_id, location=self.location)
        
        
        self.prompt = """You are a skilled assistant specializing in extracting specific fields from the text of insurance card documents.

                     Objective:
                    Extract the required information from the provided text and format it in the specified JSON structure.

                    Guidelines:
                    - Carefully review the text to identify and extract the required fields.
                    - For fields not present in the document or containing "null" (case insensitive), set their value to `""`.
                    - Do **not** return "null" or any variations of it under any condition.
                    - **Ensure the extracted Insurance Name is clean**:
                    - Remove unwanted characters like `\n`, extra spaces, or trailing text.
                    - The Insurance Name should match the official name exactly (e.g., `"United Healthcare"` 
                    instead of `"United\nHealthcare"` or `"Aetna"` instead of `"aetnaR"`).
                    - Do **not** include prefixes, suffixes, or symbols not part of the official name.
                    - Pay special attention to variations in terminology:
                    - `"Med group number"` might appear as `"GRP."`.
                    - `"Insurance Address"` could be phrased as `"Send claims to"`, `"Standard claims"`, `"Provider medical claims"`, `"Medical claims"`, or similar terms.
                    - "Id" can be written in the card 'id' or 'member id' or something like that. 
                    - Addresses often start with `"PO Box"` followed by any number of digits. Extract the `"PO Box <number>"` part separately.

                    Output Format:  
                    ```json
                    {
                        "Insurance Name": "<Extracted clean insurance name or ''>",
                        "Id": "<Extracted id(member id or id) or ''>",
                        "Patient Name": "<Extracted patient name or ''>",
                        "Plan#": "<Extracted plan number or ''>",
                        "Issuer": "<Extracted issuer number or ''>",
                        "GRP#": "<Extracted group number or ''>",
                        "Expiry Date": "<Extracted expiry date or ''>",
                        "Insurance Address": "<Extracted insurance address or ''>",
                        "State": "<Extracted state from insurance address or ''>",
                        "Insurance Address Po Box": "<Extracted 'PO Box <number>' or ''>"
                    }
        """
        self.license_prompt = """

                You are a document processor skilled in extracting specific information from text and organizing it in JSON format.

                Objective:
                Extract the specified fields from the provided document text. If a field cannot be found, include it in the output JSON with a value of ''.

                Task Details:
                Search for the fields listed below in the document text.
                Use the JSON structure provided to format the extracted information.
                For partially available fields (e.g., only First Name is present while Last Name is missing), include the available part and set the missing part to Null.
                JSON Output Template:
                
                {
                    "License #": "<Extracted License Number or ''>",
                    "First Name": "<Extracted First Name or ''>",
                    "Middle Name": "<Extracted Middle Name or ''>",  # Optional field, can be '' if not found
                    "Last Name": "<Extracted Last Name or ''>",
                    "DOB": "<Extracted Date of Birth or ''>",
                    "City": "<Extracted City or ''>",
                    "State": "<Extracted State or ''>",
                    "Zip Code": "<Extracted Zip Code or ''>",
                    "Issue Date": "<Extracted Issue Date or ''>",
                    "Expiry Date": "<Extracted Expiry Date or ''>",
                    "Gender": "<Extracted Gender or ''>",
                    "Class": "<Extracted Class or ''>",
                    "Address": "<Extracted Full Address including city name zip code as address could span mutiple linesor ''>" if there was /n in the address replace it with a space
                }
                Example Output:
                If none of the specified fields are found in the document text, the response should look like this:

                {
                    "License #": '',
                    "First Name": '',
                    "Middle Name": '',
                    "Last Name": '',
                    "DOB": '',
                    "City": '',
                    "State": '',
                    "Zip Code": '',
                    "Issue Date": '',
                    "Expiry Date": '',
                    "Gender": '',
                    "Class": '',
                    "Address": ''
                }
                Guidelines:
                Focus only on the specified fields. Do not include or process extra information.
                Be accurate, ensuring that the extracted information matches the intended field.
                Additional Notes:
                Do not infer or assume information that is not explicitly stated in the text. For fields that are not present, use '' as the value.
                Follow the JSON structure provided to ensure consistency in the output.

"""

    def upload_pdf_to_gcs(self, local_pdf_path):
        """Uploads a PDF to Google Cloud Storage and returns the GCS URI."""
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            destination_blob_name = f"{self.upload_folder}/{os.path.basename(local_pdf_path)}"
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(local_pdf_path)
            
            gcs_uri = f"gs://{self.bucket_name}/{destination_blob_name}"
            logger.info(f"Uploaded PDF to {gcs_uri}")
            return gcs_uri
        except Exception as e:
            logger.error(f"Failed to upload PDF to GCS: {e}")
            return None

    def generate_gemini_response_with_retries(self, gcs_uri, prompt, retries=2, initial_delay=1):
        """Attempt to generate a response using Gemini with retries on failure."""
        attempt = 0
        delay = initial_delay

        while attempt < retries:
            try:
                model = GenerativeModel("gemini-2.5-flash-preview-05-20")  # Updated to latest Gemini 2.0 model
                if gcs_uri.split('.')[-1].lower() == 'pdf':
                    pdf_file = Part.from_uri(uri=gcs_uri, mime_type="application/pdf")
                if gcs_uri.split('.')[-1].lower() in ['jpg', 'png', 'jpeg', 'webp']:
                    pdf_file = Part.from_uri(uri=gcs_uri, mime_type=f"image/{gcs_uri.split('.')[-1].lower()}")
               
                contents = [pdf_file, prompt]
                
                response = model.generate_content(contents, safety_settings=safety_config)
                if not response or not response.text.strip():
                    logger.warning("Gemini returned an empty response.")
                    return None
                
                logger.info("Gemini response received successfully.")
                return response.text

            except Exception as e:
                logger.error(f"Error generating Gemini response (attempt {attempt + 1}): {e}")
                time.sleep(delay)
                delay *= 2
                attempt += 1

        logger.error("Max retries reached. Unable to generate Gemini response.")
        return None

    def process_pdf_with_gemini(self, pdf_path, is_license):
        """Uploads a PDF to GCS and generates a Gemini response."""
        
        try:
            gcs_uri = self.upload_pdf_to_gcs(pdf_path)
            
            if not gcs_uri:
                logger.error("PDF upload failed; cannot proceed with Gemini processing.")
                return None
            if is_license:
                gemini_response_text = self.generate_gemini_response_with_retries(gcs_uri, prompt = self.license_prompt)
            else:
                gemini_response_text = self.generate_gemini_response_with_retries(gcs_uri, prompt = self.prompt)
            if gemini_response_text:
                cleaned_text = re.sub(r"```json|```", "", gemini_response_text).strip()
                print("cleaned_text", cleaned_text)
                try:
                    response = json.loads(cleaned_text)
                    if is_license:
                        return response
                    elif response["Insurance Address"]: 
                        cleaned_value = re.sub(r'\s+', ' ', response["Insurance Address"]).strip()
                        response["Insurance Address"] = cleaned_value

                        logger.info("Parsed Gemini response successfully.")

                        
                        print('Response:',response)
                        return response
                    else:
                        return response
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode Gemini response as JSON: {e}")
                    return None
            else:
                logger.warning("Received an empty response from Gemini; skipping processing.")
                return None
            
        except Exception as e:
            logger.error(f"Failed to process PDF with Gemini: {e}")
            return None

    def combined_Images(self, img1, img2, outputPath):
        try:
            image1 = Image.open(img1)
            image2 = Image.open(img2)
            
            width1, height1 = image1.size
            width2, height2 = image2.size
            
            combined_width = max(width1, width2)
            combined_height = height1 + height2
            
            combined_image = Image.new("RGB", (combined_width, combined_height), (255, 255, 255))
            
            combined_image.paste(image1, (0, 0))
            combined_image.paste(image2, (0, height1))
            combine_Path = f"{outputPath}.jpg"
            combined_image.save(combine_Path)
            return combine_Path
            
        except Exception as exe:
            print(f"Error in combined_Images : {exe}")
            logger.error("Received an empty response from Gemini; skipping processing.")
            return None