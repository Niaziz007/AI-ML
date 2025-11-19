from fastapi import FastAPI, Request
from API.app.api.endpoints import user
from API.app.core.logger import logger
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORSMiddleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of origins allowed to communicate with FastAPI
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Middleware to log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response Status Code: {response.status_code}")
    return response

# Include API routers
app.include_router(user.router, prefix="/api", tags=["api"])
# app.include_router(item.router, prefix="/items", tags=["Items"])

# Log application startup and shutdown
@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application is shutting down...")
