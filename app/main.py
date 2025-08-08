from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.ui import router as ui_router
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.middleware import APIActivityMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.project_name,
    openapi_url=f'{settings.api_v1_str}/openapi.json',
)

# Set CORS - allowing all origins for development
# In production, specify actual origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Add API activity tracking middleware
app.add_middleware(APIActivityMiddleware)

# Mount static files
app.mount('/static', StaticFiles(directory='app/static'), name='static')

# Include routers
app.include_router(api_router, prefix=settings.api_v1_str)
app.include_router(ui_router)


@app.get('/health')
def health_check():
    return {'status': 'healthy'}
