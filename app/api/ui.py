from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory='app/templates')


@router.get('/')
@router.get('/dashboard')
async def dashboard(request: Request) -> Any:
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url='/dashboard/users', status_code=303)


@router.get('/dashboard/users', response_class=HTMLResponse)
async def users_tab(request: Request, db: Session = Depends(deps.get_db)) -> Any:
    users = crud.user.get_multi(db, limit=1000)
    # Sort users by username alphabetically
    users.sort(key=lambda x: x.username.lower())

    # Check if this is an HTMX request
    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'dashboard/users.html', {'request': request, 'users': users}
        )
    else:
        # Full page for direct access/refresh
        return templates.TemplateResponse(
            'dashboard/index.html',
            {
                'request': request,
                'initial_content': templates.get_template('dashboard/users.html').render(
                    request=request, users=users
                ),
                'active_tab': 'users',
            },
        )


@router.get('/dashboard/users/new', response_class=HTMLResponse)
async def new_user_form(request: Request) -> Any:
    return templates.TemplateResponse(
        'dashboard/user_form.html',
        {
            'request': request,
            'title': 'Create New User',
            'action_url': '/ui/users/create',
            'submit_text': 'Create User',
            'user': None,
        },
    )


@router.get('/dashboard/users/{user_id}', response_class=HTMLResponse)
async def user_detail(request: Request, user_id: str, db: Session = Depends(deps.get_db)) -> Any:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return templates.TemplateResponse(
        'dashboard/user_detail.html', {'request': request, 'user': user}
    )


@router.get('/dashboard/users/{user_id}/edit', response_class=HTMLResponse)
async def edit_user_form(request: Request, user_id: str, db: Session = Depends(deps.get_db)) -> Any:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return templates.TemplateResponse(
        'dashboard/user_form.html',
        {
            'request': request,
            'title': 'Update User',
            'action_url': f'/ui/users/{user_id}',
            'submit_text': 'Update User',
            'user': user,
        },
    )


@router.get('/dashboard/roles', response_class=HTMLResponse)
async def roles_tab(request: Request, db: Session = Depends(deps.get_db)) -> Any:
    roles = crud.role.get_multi(db, limit=1000)
    # Sort roles by role name alphabetically
    roles.sort(key=lambda x: x.role_name.lower())

    # Check if this is an HTMX request
    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'dashboard/roles.html', {'request': request, 'roles': roles}
        )
    else:
        # Full page for direct access/refresh
        return templates.TemplateResponse(
            'dashboard/index.html',
            {
                'request': request,
                'initial_content': templates.get_template('dashboard/roles.html').render(
                    request=request, roles=roles
                ),
                'active_tab': 'roles',
            },
        )


@router.get('/dashboard/roles/new', response_class=HTMLResponse)
async def new_role_form(request: Request, db: Session = Depends(deps.get_db)) -> Any:
    users = crud.user.get_multi(db, limit=1000)
    return templates.TemplateResponse(
        'dashboard/role_form.html',
        {
            'request': request,
            'title': 'Create New Role',
            'action_url': '/ui/roles/create',
            'submit_text': 'Create Role',
            'role': None,
            'all_users': users,
        },
    )


@router.get('/dashboard/roles/{role_id}', response_class=HTMLResponse)
async def role_detail(request: Request, role_id: str, db: Session = Depends(deps.get_db)) -> Any:
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail='Role not found')
    return templates.TemplateResponse(
        'dashboard/role_detail.html', {'request': request, 'role': role}
    )


@router.get('/dashboard/roles/{role_id}/edit', response_class=HTMLResponse)
async def edit_role_form(request: Request, role_id: str, db: Session = Depends(deps.get_db)) -> Any:
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail='Role not found')
    users = crud.user.get_multi(db, limit=1000)
    return templates.TemplateResponse(
        'dashboard/role_form.html',
        {
            'request': request,
            'title': 'Update Role',
            'action_url': f'/ui/roles/{role_id}',
            'submit_text': 'Update Role',
            'role': role,
            'all_users': users,
        },
    )


@router.get('/dashboard/secrets', response_class=HTMLResponse)
async def secrets_tab(request: Request, db: Session = Depends(deps.get_db)) -> Any:
    tokens = crud.token.get_multi(db, limit=1000)

    # Check if this is an HTMX request
    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'dashboard/secrets.html', {'request': request, 'tokens': tokens}
        )
    else:
        # Full page for direct access/refresh
        return templates.TemplateResponse(
            'dashboard/index.html',
            {
                'request': request,
                'initial_content': templates.get_template('dashboard/secrets.html').render(
                    request=request, tokens=tokens
                ),
                'active_tab': 'secrets',
            },
        )


@router.get('/dashboard/secrets/{token_id}', response_class=HTMLResponse)
async def secret_detail(request: Request, token_id: str, db: Session = Depends(deps.get_db)) -> Any:
    token = crud.token.get(db, id=token_id)
    if not token:
        raise HTTPException(status_code=404, detail='Token not found')
    activities = crud.activity.get_by_token(db, token_id=token_id, limit=100)
    return templates.TemplateResponse(
        'dashboard/secret_detail.html',
        {'request': request, 'token': token, 'activities': activities},
    )


# Validation endpoints for HTMX
@router.post('/validate/name', response_class=HTMLResponse)
async def validate_name(request: Request) -> str:
    form = await request.form()
    # Get the field name from the form data (could be first_name or last_name)
    name = form.get('first_name') or form.get('last_name') or ''

    if name and not name.replace(' ', '').isalpha():
        return '<span class="text-red-600">Names must contain only letters</span>'
    return ''


@router.post('/validate/email', response_class=HTMLResponse)
async def validate_email(email: str = Form(...), db: Session = Depends(deps.get_db)) -> str:
    import re

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return '<span class="text-red-600">Invalid email format</span>'

    # Check if email already exists
    existing = crud.user.get_by_email(db, email=email)
    if existing:
        return '<span class="text-red-600">Email already exists</span>'

    return ''


@router.post('/api/v1/secrets/htmx', response_class=HTMLResponse)
async def create_secret_htmx(db: Session = Depends(deps.get_db)) -> str:
    # Create token
    token = crud.token.create(db)

    # Return HTML response for HTMX
    return f"""
    <div class="rounded-md bg-green-50 p-4">
        <div class="flex">
            <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
            </div>
            <div class="ml-3">
                <h3 class="text-sm font-medium text-green-800">Token Generated Successfully</h3>
                <div class="mt-2 text-sm text-green-700">
                    <p class="font-medium">Copy this token now - it won't be shown again:</p>
                    <code class="block mt-1 bg-green-100 px-2 py-1 rounded text-xs break-all">{token.token}</code>
                </div>
                <div class="mt-4">
                    <button 
                        hx-get="/dashboard/secrets"
                        hx-target="#tab-content"
                        hx-swap="innerHTML"
                        class="text-sm font-medium text-green-800 hover:text-green-700">
                        Refresh token list
                    </button>
                </div>
            </div>
        </div>
    </div>
    """


# UI form handlers (no authentication required)
@router.post('/ui/users/create', response_class=HTMLResponse)
async def create_user_ui(request: Request, db: Session = Depends(deps.get_db)) -> Any:
    form = await request.form()

    # Extract form data
    user_data = schemas.UserCreate(
        first_name=form.get('first_name'), last_name=form.get('last_name'), email=form.get('email')
    )

    # Check if email already exists
    if crud.user.get_by_email(db, email=user_data.email):
        # Return error response
        return templates.TemplateResponse(
            'dashboard/error.html',
            {'request': request, 'error': 'A user with this email already exists.'},
        )

    # Create user
    user = crud.user.create(db, obj_in=user_data)

    # Check if password was generated
    generated_password = getattr(user, 'generated_password', None)

    # Return updated users list with success message
    users = crud.user.get_multi(db, limit=1000)

    if generated_password:
        # Return a response that includes the generated password
        return f"""
        <div class="rounded-md bg-green-50 p-4 mb-4">
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="ml-3">
                    <h3 class="text-sm font-medium text-green-800">User Created Successfully</h3>
                    <div class="mt-2 text-sm text-green-700">
                        <p>Username: <strong>{user.username}</strong></p>
                        <p>Generated Password: <strong>{generated_password}</strong></p>
                        <p class="mt-1 text-xs">Save this password - it won't be shown again!</p>
                    </div>
                </div>
            </div>
        </div>
        """ + templates.get_template('dashboard/users.html').render(request=request, users=users)
    else:
        return templates.TemplateResponse(
            'dashboard/users.html', {'request': request, 'users': users}
        )


@router.post('/ui/users/{user_id}', response_class=HTMLResponse)
async def update_user_ui(request: Request, user_id: str, db: Session = Depends(deps.get_db)) -> Any:
    form = await request.form()

    user = crud.user.get(db, id=user_id)
    if not user:
        return templates.TemplateResponse(
            'dashboard/error.html', {'request': request, 'error': 'User not found'}
        )

    # Build update data
    update_data = {}
    if form.get('first_name'):
        update_data['first_name'] = form.get('first_name')
    if form.get('last_name'):
        update_data['last_name'] = form.get('last_name')
    if form.get('email'):
        update_data['email'] = form.get('email')
    if form.get('status') and form.get('status') in ['active', 'disabled', 'terminated']:
        update_data['status'] = form.get('status')

    # Update display_name if names are changed
    if 'first_name' in update_data or 'last_name' in update_data:
        first_name = update_data.get('first_name', user.first_name)
        last_name = update_data.get('last_name', user.last_name)
        update_data['display_name'] = f'{first_name} {last_name}'

    # Update user
    user = crud.user.update(db, db_obj=user, obj_in=update_data)

    # Return updated users list
    users = crud.user.get_multi(db, limit=1000)
    # Sort users by username alphabetically
    users.sort(key=lambda x: x.username.lower())
    return templates.TemplateResponse('dashboard/users.html', {'request': request, 'users': users})


@router.delete('/ui/users/{user_id}', response_class=HTMLResponse)
async def delete_user_ui(user_id: str, db: Session = Depends(deps.get_db)) -> str:
    user = crud.user.get(db, id=user_id)
    if not user:
        return '<div class="text-red-600">User not found</div>'

    crud.user.remove(db, id=user_id)
    # Return empty response for HTMX to remove the row
    return ''


@router.post('/ui/roles/create', response_class=HTMLResponse)
async def create_role_ui(request: Request, db: Session = Depends(deps.get_db)) -> Any:
    form = await request.form()

    # Extract form data
    role_data = schemas.RoleCreate(
        role_name=form.get('role_name'), role_description=form.get('role_description')
    )

    # Check if role name already exists
    if crud.role.get_by_name(db, role_name=role_data.role_name):
        # Return error response
        return templates.TemplateResponse(
            'dashboard/error.html',
            {'request': request, 'error': 'A role with this name already exists.'},
        )

    # Create role
    crud.role.create(db, obj_in=role_data)

    # Return updated roles list
    roles = crud.role.get_multi(db, limit=1000)
    # Sort roles by role name alphabetically
    roles.sort(key=lambda x: x.role_name.lower())
    return templates.TemplateResponse('dashboard/roles.html', {'request': request, 'roles': roles})


@router.post('/ui/roles/{role_id}', response_class=HTMLResponse)
async def update_role_ui(request: Request, role_id: str, db: Session = Depends(deps.get_db)) -> Any:
    form = await request.form()

    role = crud.role.get(db, id=role_id)
    if not role:
        return templates.TemplateResponse(
            'dashboard/error.html', {'request': request, 'error': 'Role not found'}
        )

    # Build update data
    update_data = {}
    if form.get('role_name'):
        update_data['role_name'] = form.get('role_name')
    if form.get('role_description') is not None:  # Allow empty description
        update_data['role_description'] = form.get('role_description')

    # Update role
    if update_data:
        role = crud.role.update(db, db_obj=role, obj_in=update_data)

    # Update user assignments
    user_ids = form.getlist('user_ids')
    if user_ids is not None:
        role = crud.role.update_users(db, db_obj=role, user_ids=user_ids)

    # Return updated roles list
    roles = crud.role.get_multi(db, limit=1000)
    # Sort roles by role name alphabetically
    roles.sort(key=lambda x: x.role_name.lower())
    return templates.TemplateResponse('dashboard/roles.html', {'request': request, 'roles': roles})
