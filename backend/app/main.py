from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from app.api import tickets, auth
from app.core.database import init_db
from app.core.config import settings
import uvicorn
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Depends

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Define a middleware to handle both trailing slash and non-trailing slash routes
class TrailingSlashMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check if this was already handled to prevent infinite recursion
        if request.scope.get("_trailing_slash_handled", False):
            return await call_next(request)
            
        # Process the request normally first
        response = await call_next(request)
        
        # If we get a 404, check if adding/removing a trailing slash helps
        if response.status_code == 404:
            path = request.url.path
            original_path = path
            
            # Try the other version of the path (with or without trailing slash)
            if path.endswith('/'):
                # Try without trailing slash
                request.scope["path"] = path[:-1]
                logger.info(f"Trying path without trailing slash: {request.scope['path']}")
            else:
                # Try with trailing slash
                request.scope["path"] = f"{path}/"
                logger.info(f"Trying path with trailing slash: {request.scope['path']}")
                
            # Mark as handled to prevent infinite recursion
            request.scope["_trailing_slash_handled"] = True
            
            # Ensure we're preserving any authorization headers in the request
            if "authorization" in request.headers:
                auth_header = request.headers.get("authorization")
                logger.info(f"Preserving authorization header during trailing slash handling: {auth_header[:15]}...")
                # Make sure the authorization is preserved in the scope
                if "headers" in request.scope:
                    request.scope["headers"] = [(k, v) for k, v in request.scope["headers"] if k.decode("latin1").lower() != "authorization"]
                    request.scope["headers"].append((b"authorization", auth_header.encode("latin1")))
            
            # Try the alternative path
            response = await call_next(request)
            
            if response.status_code != 404:
                logger.info(f"Successfully handled request by changing path from {original_path} to {request.scope['path']}")
                
        return response

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    Modern helpdesk system API.
    
    ## Trailing Slashes
    This API handles both trailing slash and non-trailing slash paths identically.
    For example, both `/api/v1/tickets/` and `/api/v1/tickets` will work.
    
    ## Authentication
    Most endpoints require authentication via a Bearer JWT token.
    """,
    version="1.0.0"
)

# Add trailing slash middleware
app.add_middleware(TrailingSlashMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add additional logging for authentication debugging
@app.middleware("http")
async def auth_debugging_middleware(request: Request, call_next):
    # Log authentication headers for debugging
    auth_header = request.headers.get("Authorization", "No auth header")
    logger.debug(f"Request to {request.url.path} with auth: {auth_header[:15]}..." if len(auth_header) > 15 else auth_header)
    
    response = await call_next(request)
    
    if response.status_code in [401, 403]:
        logger.warning(f"Auth failure: {request.url.path} returned {response.status_code}")
    
    return response

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "status_code": 422, "message": "Validation error"},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error with traceback
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500},
    )

# Debug route to test API access
@app.get(f"{settings.API_V1_STR}/debug")
async def debug_route():
    return {"status": "API is accessible", "prefix": settings.API_V1_STR}

# Debug endpoint for admin auth testing
@app.get(f"{settings.API_V1_STR}/debug-admin")
async def debug_admin(current_user = Depends(auth.current_active_user)):
    return {
        "status": "authenticated", 
        "user": current_user.email,
        "is_admin": current_user.is_superuser,
        "user_id": current_user.id
    }

# Add health check endpoint for monitoring
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "api_prefix": settings.API_V1_STR
    }

# Include routers with correct prefixes
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(tickets.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_prefix": settings.API_V1_STR
    }

@app.get("/api")
async def api_root():
    return {
        "message": "API v1 is available at " + settings.API_V1_STR,
        "status": "online"
    }

@app.get(settings.API_V1_STR)
async def api_v1_root():
    return {
        "message": "API v1 endpoints available",
        "endpoints": [
            f"{settings.API_V1_STR}/auth/login",
            f"{settings.API_V1_STR}/auth/register",
            f"{settings.API_V1_STR}/tickets",
            f"{settings.API_V1_STR}/users"
        ],
        "docs_url": "/docs"
    }

@app.on_event("startup")
async def startup_event():
    await init_db()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
