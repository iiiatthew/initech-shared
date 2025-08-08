from fastapi import APIRouter

from app.api.v1.endpoints import roles, users

api_router = APIRouter()

# All endpoints use plural form for consistency
# /users endpoints (all CRUD operations)
api_router.include_router(users.router, prefix='/users', tags=['users'])

# /roles endpoints (all CRUD operations)
api_router.include_router(roles.router, prefix='/roles', tags=['roles'])
