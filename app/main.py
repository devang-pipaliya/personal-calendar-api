"""
Main file contains project instance
"""

from uuid import uuid4

from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from app.common.db_utils import db
from app.core.deps import get_current_user
from app.core.utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password
)
from app.entity.schemas import UserOut, UserAuth, TokenSchema, SystemUser
from app.entity.users import User


meeting_app = FastAPI(docs_url=None, redoc_url=None)


origins = [
    "http://localhost",
    "http://localhost:3000",
]

meeting_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@meeting_app.get("/", summary="Testing only :) ")
async def test():
    return ({"success": True})


@meeting_app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=meeting_app.openapi_url,
        title=meeting_app.title + " - Swagger UI",
        oauth2_redirect_url=meeting_app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


@meeting_app.get(meeting_app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@meeting_app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=meeting_app.openapi_url,
        title=meeting_app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
    )


@meeting_app.get("/users/{username}")
async def read_user(username: str):
    return {"message": f"Hello {username}"}


@meeting_app.post('/signup',
    summary="Create new user",
    # response_model=UserOut
)
async def create_user(data: UserAuth):
    # querying database to check if user already exist
    # user =
    user_obj = User()
    user = user_obj.get_single_record({'email': data.email})
    print(f"user-> {user}")
    if user is not None:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    user = {
        'email': data.email,
        'password': get_hashed_password(data.password),
        'userid': str(uuid4())
    }
    user = user_obj.create_record(user)    # saving user to database
    return user


@meeting_app.post('/login',
    summary="Create access and refresh tokens for user",
    response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm=Depends()):
    user_obj = User()
    user = user_obj.get_single_record({'email': form_data.username})
    # user = db.get(form_data.username, None)
    print(f"user-> {user}")
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user['password']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_access_token(user['email']),
        "refresh_token": create_refresh_token(user['email']),
    }


@meeting_app.get('/me',
    summary='Get details of currently logged in user',
    response_model=UserOut)
async def get_me(user: SystemUser=Depends(get_current_user)):
    return user


@meeting_app.get('/users',
    summary='Get details of currently logged in user',
    # response_model=list[User])
)
def get_users():
    usr_lst = []
    users = User().get_records()
    for usr in users:
        usr_lst.append(usr)
    # print(f"{usr_lst}")
    # return users
    return usr_lst
