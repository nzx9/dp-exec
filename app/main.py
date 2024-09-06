from db.psql_connector import DB
from fastapi import FastAPI, Depends, Request, Response, status
from dotenv import dotenv_values
from typing import List

# Auth
from auth.auth_handler import (
    AuthHandler,
    LoginUserModel,
    RegisterUserModel,
    get_current_active_user_jwt as get_current_active_user,
    get_current_active_user_api_key,
    User,
)
from auth.auth_bearer import JWTBearer, APIKey
from auth.api_key_handler import APIKeyManager
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

# Types
from type_def.common import Error, Success
from type_def.auth import APIKeyReq, ChangePasswordModel
from type_def.data import UserData


# Spark

from api.v1.process import paginate_rdd_data, process_large_data, sc
# from fastapi.security import APIKeyHeader

app = FastAPI()
config = dotenv_values(".env")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# auth_handler = AuthHandler()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.mount("/models", StaticFiles(directory="models"), name="models")


@app.get("/")
async def root():
    return {"msg": "Welcome to Querio REST API"}


@app.get("/ping")
async def ping():
    return "pong"


#########################
#      AUTH ROUTES     #
########################
@app.post("/auth/login", tags=["auth"])
async def login(login_model: LoginUserModel):
    res = await AuthHandler().login(login_model)
    return res.response()


@app.post("/auth/register", tags=["auth"])
async def register(register_model: RegisterUserModel):
    res = await AuthHandler().register(register_model)
    return res.response()


@app.get("/auth/users/me", tags=["auth"], dependencies=[Depends(JWTBearer())])
async def read_users_me(
    response: Response,
    current_user: User = Depends(get_current_active_user),
):
    return (
        Success("Successfull", status.HTTP_200_OK, current_user.pub()).resp(response)
        if current_user
        else Error("User not found", 4004, 404).resp(response)
    )


@app.get("/auth/logout", tags=["auth"], dependencies=[Depends(JWTBearer())])
async def logout(current_user: User = Depends(get_current_active_user)):
    return {"msg": "Logout"}


@app.put(
    "/auth/change-password/{user_id}",
    tags=["auth"],
    dependencies=[Depends(JWTBearer())],
)
async def change_password(
    user_id: str,
    body: ChangePasswordModel,
    current_user: User = Depends(get_current_active_user),
):
    return (
        await AuthHandler(current_user).change_password(
            user_id, body.new_password, body.curr_password
        )
    ).response()


@app.get("/auth/delete/{user_id}", dependencies=[Depends(JWTBearer())])
async def delete_user(
    response: Response,
    user_id: str,
    current_user: User | None = Depends(get_current_active_user),
):
    return (
        Success("User deleted successfully", status.HTTP_200_OK, {}).resp(response)
        if AuthHandler(current_user).delete_user(user_id)
        else Error(
            "Something went wrong, while deleting user",
            4005,
            status.HTTP_400_BAD_REQUEST,
        ).resp(response)
    )


@app.post("/auth/token/api/new", tags=["auth"], dependencies=[Depends(JWTBearer)])
async def new_api_token(
    response: Response, body: APIKeyReq, user: User = Depends(get_current_active_user)
):
    return APIKeyManager(user).issue_new(body).resp(response)


@app.post("/auth/token/api/check/{api_key}", tags=["auth"])
async def check_api_token(api_key: str, scope: str = None):
    origin = None
    valid = APIKeyManager().safe_check(api_key, scope=scope, origin=origin)
    if valid:
        return Success("Validation passed", 200, {})
    return Error("Validation failed", 401, 4001)


@app.delete(
    "/auth/token/api/delete/{api_key}", tags=["auth"], dependencies=[Depends(JWTBearer)]
)
async def delete_api_token(api_key: str):
    return {"msg": "Delete API Token"}


@app.get("/auth/token/api/list", tags=["auth"], dependencies=[Depends(JWTBearer)])
async def list_api_token(
    response: Response, user: User = Depends(get_current_active_user)
):
    return APIKeyManager(user).get_my_token_list().resp(response)

################################
# LARGE DATA PROCESSING ROUTES #
################################

@app.post("/process/")
async def process_data(data: List[UserData], user: User = Depends(get_current_active_user_api_key)):
    """
    Endpoint to process incoming data.
    """
    db = DB()
    if(user.access == "write"):
        for entry in data:
            db.exec("INSERT INTO items (item_id, quantity, price, user_id) VALUES (%s, %s, %s, %s)",
                (entry['item_id'], entry['quantity'], entry['price'], user.id))

        return Success("success", 200, None)

@app.get("/aggregate/")
async def aggregate_data(user: User = Depends(get_current_active_user_api_key)):
    """
    Endpoint to process and aggregate data using map-reduce.
    """
    db = DB()
    # Validate access level
    if user.access == "read":
        data = db.exec("SELECT * FROM items")

        result = process_large_data(data)
        return Success("Success" ,200, {"aggregated_data": result})
    return Error("No access")

@app.get("/paginate/")
async def paginate_data(page: int = 1, page_size: int = 10, user: User = Depends(get_current_active_user)):
    """
    Endpoint to paginate large data.
    """
    db = DB()

    if user.access == "read":
        data = db.exec("SELECT * FROM items")

        rdd = sc.parallelize(data)

        paginated_result = paginate_rdd_data(rdd, page, page_size)
        return Success("Success", 200, {"page": page, "data": paginated_result})
    else:
        return Error("No access", 4000, 400)

#########################
#     TEST ROUTES       #
#########################
@app.get("/check-headers")
async def check_headers(request: Request, body: dict | None = None, param: str | None = None):
    return {"headers": request.headers, "body": body, "param": param}

@app.get("/api/v1/test/error", tags=["test-error"])
async def run_test_error(response: Response) -> None:
    return Error("Error", 2000, status.HTTP_400_BAD_REQUEST).resp(response)

@app.get(
    "/api/v1/test/success",
    tags=["test-success"],
    dependencies=[Depends(APIKey())],
)
async def run_test_success(request: Request, response: Response) -> None:
    return Success("Success", status.HTTP_200_OK, {}).resp(response)


