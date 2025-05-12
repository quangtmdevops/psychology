from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from app.core.database import engine, Base
from app.routers import users, groups, posts, test
from app.core.auth import get_current_user
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema, Token, UserLogin
from app.schemas.test import TestInDB, TestAnswerCreate, EntityInDB, TestAnswerInDB

# Create database tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Psychology API",
    description="""
    API for Psychology Application.
    
    ## Authentication
    
    This API uses JWT Bearer token authentication. To use the API:
    
    1. Register a new user at `/api/v1/users/register`
    2. Get a token at `/api/v1/users/token`
    3. Use the token in the Authorization header: `Bearer your_token_here`
    
    ## Scopes
    
    The API uses the following scopes:
    - `users:read`: Read user information
    - `users:write`: Modify user information
    - `users:delete`: Delete user account
    
    Regular users get `users:read` scope, while premium users get all scopes.
    """,
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with authentication
app.include_router(users, prefix="/api/v1")
app.include_router(groups, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(posts, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(test, prefix="/api/v1", dependencies=[Depends(get_current_user)])


# Custom OpenAPI schema with security scheme
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme only, let FastAPI handle schemas
    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": """
            Enter your JWT token in the format: `Bearer your_token_here`
            
            To get a token:
            1. Register at `/api/v1/users/register`
            2. Get token at `/api/v1/users/token`
            3. Use the token in the Authorization header
            """
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"Bearer": []}]
    
    # Add example request bodies
    openapi_schema["components"]["examples"] = {
        "UserRegistration": {
            "value": {
                "email": "user@example.com",
                "password": "password123"
            }
        },
        "UserLogin": {
            "value": {
                "email": "user@example.com",
                "password": "password123"
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "docExpansion": "none",
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "syntaxHighlight.theme": "monokai",
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "tryItOutEnabled": True,
        }
    )

@app.get("/")
async def root():
    return {"message": "Welcome to Psychology API"}

def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user

def premium_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_premium:
        raise HTTPException(status_code=403, detail="Premium only")
    return current_user
