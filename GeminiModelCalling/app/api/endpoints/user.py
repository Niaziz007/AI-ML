from fastapi import APIRouter, Request, File, UploadFile, HTTPException, Form
from API.app.core.logger import logger
from API.app.core.config import get_db_connection
from API.app.LLM.Gemini import GCSGeminiHandler
from API.app.service.user_service import *
from fastapi.responses import JSONResponse
from fastapi.responses import Response
import os
from pathlib import Path
import shutil
import pandas as pd
import re
from API.app.core.config import * 

router = APIRouter()



UPLOAD_FOLDER = Path("app/api/endpoints/File")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def fetch_insurance_data(insurance_address=None, payer_description=None, Provider_Code=None, State=None):
    """
    Fetches insurance data based on Insurance Address, Payer Description, and Provider Code.

    Parameters:
        insurance_address (str, optional): Insurance Address filter.
        payer_description (str, optional): Payer Description filter.
        Provider_Code (int, optional): Billing Physician's Provider Code.
        State (State of the insurance)

    Returns:
        list[dict]: Query results in JSON format.
    """
    conn = get_db_connection('NJ76')

    base_query = """
    SELECT TOP 1 COUNT(*) AS claim_count, ig.InsGroup_Id, ig.InsGroup_Name, ci.Insurance_Id  
    FROM Claim_Insurance ci 
    JOIN Claims c ON ci.Claim_No = c.Claim_No 
    JOIN Insurances i WITH (NOLOCK, NOWAIT) ON ci.Insurance_Id = i.Insurance_Id 
    JOIN Insurance_Payers ip WITH (NOLOCK, NOWAIT) ON i.InsPayer_Id = ip.InsPayer_Id
    JOIN insurance_names ins WITH (NOLOCK, NOWAIT) ON ip.InsName_Id = ins.InsName_Id 
    JOIN Insurance_Groups ig WITH (NOLOCK, NOWAIT) ON ig.InsGroup_Id = ins.InsGroup_Id 
    JOIN Provider_Payers pp WITH (NOLOCK, NOWAIT) ON pp.InsPayer_Id = i.InsPayer_Id 
    AND c.Billing_Physician = pp.Provider_Code 
    WHERE ISNULL(c.Deleted, 0) = 0 
    AND ISNULL(ci.Deleted, 0) = 0 
    """
    if Provider_Code:
        base_query += f" AND c.Billing_Physician = {Provider_Code}"   
    if insurance_address:
        base_query += f" AND i.Insurance_Address = '{insurance_address}'"
    if payer_description:
        base_query += f" AND ip.InsPayer_Description LIKE '%{payer_description}%'"
    if State:
        base_query += f" AND i.Insurance_State =  '{State}'"
    base_query += """
    GROUP BY ci.Insurance_Id, ig.InsGroup_Id, ig.InsGroup_Name 
    ORDER BY claim_count DESC
    """

    print("Executing SQL Query:")
    print(base_query)

    df = pd.read_sql(base_query, conn)
    conn.close()
    return df.to_dict(orient='records')

@router.get("/")
def Welcome(request: Request):
    logger.info(f"URL: {request.url} in user called ")
    msg= {"message": "Insurance Card API working fine"}
    return msg

@router.post("/getData")
def get_data(
    request: Request,
    frontfile: UploadFile = File(None),
    backfile: UploadFile = File(None),
    Provider_Code: int = Form(...),
):
    file_Name = None
    frontfile_Path = None
    backfile_Path = None
    pdf_path = None 
 
    try:
        logger.info(f"URL: {request.url} invoked by user.")
 
        if not (frontfile and backfile) or not Provider_Code:
            logger.error("Both frontfile and backfile and Provider Code must be provided.")
            raise HTTPException(
                status_code=400,
                detail="Both frontfile and backfile and Provider Code must be provided."
            )

        # Validate file types
        allowed_image_types = ["image/jpeg", "image/png", "image/jpg"]
 
        # if pdffile:
        #     if pdffile.content_type not in allowed_image_types:
        #         logger.error("Unsupported PDF file type uploaded.")
        #         raise HTTPException(
        #             status_code=400,
        #             detail="Only PDF files are supported for the 'pdffile' field.",
        #         )
        #     # Handle PDF file upload
        #     pdf_path = handleFile(pdffile)
        # else:
        if (
            frontfile.content_type not in allowed_image_types
            or backfile.content_type not in allowed_image_types
        ):
            logger.error("Unsupported image file types uploaded.")
            raise HTTPException(
                status_code=400,
                detail="Only JPEG and PNG files are supported for images.",
            )
        # Handle image file uploads
        frontfile_Path = handleFile(frontfile)
        backfile_Path = handleFile(backfile)

        # Combine or process based on file type
        GGH = GCSGeminiHandler()
        # if pdffile:
        #     # Process the PDF file with Gemini
        #     file_Name = pdf_path
        #     response = GGH.process_pdf_with_gemini(file_Name, 0)
        #     response=fetch_insurance_data(insurance_address=response['Insurance Address Po Box'], payer_description=response['Insurance Name'], Provider_Code = Provider_Code)
        # else:
        # Combine images
        combined_image_path = "API/File/Combine_Images"
        file_Name = GGH.combined_Images(frontfile_Path, backfile_Path, combined_image_path)
        # Process the combined image with Gemini
        response = GGH.process_pdf_with_gemini(file_Name, 0)

        response['Insurance Address Po Box'] = response['Insurance Address Po Box'].replace('.', '')

        response1 = fetch_insurance_data(insurance_address=response['Insurance Address Po Box'],
            payer_description=response['Insurance Name'], Provider_Code = Provider_Code)

        if len(response1) <= 0:
            response1 = fetch_insurance_data(insurance_address=response['Insurance Address Po Box'],
                payer_description=response['Insurance Name'].split(' ')[0], Provider_Code = Provider_Code)
        
        if len(response1) > 0: 
            response1[0]['Insurance Name'] = response['Insurance Name']
            response1[0]['Policy Number'] = response['Id']
 
        logger.info(f"Gemini response for {file_Name}: {response1}")
        responses = JSONResponse(content={"Data": response1})
        responses.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        responses.headers['X-Content-Type-Options'] = 'nosniff'
        responses.headers['X-Frame-Options'] = 'SAMEORIGIN'
        responses.headers['X-XSS-Protection'] = '1; mode=block'
        responses.headers['Server'] = '' 
        return responses 
    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(
            status_code=404, detail="File not found. Please check the upload."
        )
    except Exception as e:
        logger.error(f"Unexpected error handling request for {file_Name}: {e}")
        raise HTTPException(
            status_code=500, detail="Unexpected error occurred."
        )
    finally:
        # Cleanup temporary files
        if frontfile_Path and os.path.exists(frontfile_Path):
            os.remove(frontfile_Path)
        if backfile_Path and os.path.exists(backfile_Path):
            os.remove(backfile_Path)
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)
        if file_Name and os.path.exists(file_Name):
            os.remove(file_Name)

@router.post("/getLicenseData")
def get_license_data(request: Request,pdf:UploadFile=File(None)):
    file_Name = None
      # Initialize to avoid referencing before assignment in error handling
    try:
        logger.info(f"URL: {request.url} in user called")
        
        # Ensure at least one input is provided
        if not pdf :
            logger.error("No file  data provided.")
            raise HTTPException(
                status_code=400, detail="Either 'file'  must be provided.")
        
        logger.info("Handling PDF File ")
        file_Name = handleFile(pdf)
    
        # Process the file with Gemini Handler
        GGH = GCSGeminiHandler()
        response = GGH.process_pdf_with_gemini(file_Name, 1)
        logger.info(f"Results from Gemini for image {file_Name} Res = {response}")
       
        responses= JSONResponse(content={"Data": response})
        responses.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        responses.headers['X-Content-Type-Options'] = 'nosniff'
        responses.headers['X-Frame-Options'] = 'SAMEORIGIN'
        responses.headers['X-XSS-Protection'] = '1; mode=block'
        responses.headers['server'] = '' 
        return responses 

    except HTTPException as e:
        # Capture already raised HTTPExceptions
        logger.error(f"HTTPException: {e.detail}")
        raise
    except FileNotFoundError as e:
        logger.error(f"File not found error: {e}")
        raise HTTPException(
            status_code=404, detail="File not found. Please check the upload."
        )
    except Exception as e:
        logger.error(f"Unexpected error handling request for {file_Name}: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")