from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
import hashlib

from app.server.database import (
    add_user,
    delete_user,
    retrieve_user,
    retrieve_users,
    update_user,
)
from app.server.models.user import (
    ErrorResponseModel,
    ResponseModel,
    UserIn,
    UserOut,
    UserInDB,
    UpdateUserModel,
)

router = APIRouter()

def secure_password_hasher(raw_password: str):
    encoded_passwd = raw_password.encode()
    return hashlib.sha256(encoded_passwd).hexdigest()
def secure_save_user(user_in: UserIn):
    hashed_password = secure_password_hasher(user_in.password)
    print(hashed_password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db

@router.post("/", response_description="user data added into the database", response_model=UserOut)
async def add_user_data(user: UserIn = Body(...)):
    user_secue = secure_save_user(user)
    user_json = jsonable_encoder(user_secue)
    new_user = await add_user(user_json)
    return new_user


@router.get("/", response_description="users retrieved")
async def get_users():
    users = await retrieve_users()
    if users:
        return ResponseModel(users, "users data retrieved successfully")
    return ResponseModel(users, "Empty list returned")


@router.get("/{id}", response_description="user data retrieved")
async def get_user_data(id):
    user = await retrieve_user(id)
    if user:
        return ResponseModel(user, "user data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "user doesn't exist.")


@router.put("/{id}")
async def update_user_data(id: str, req: UpdateUserModel = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_user = await update_user(id, req)
    if updated_user:
        return ResponseModel(
            "user with ID: {} name update is successful".format(id),
            "user name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the user data.",
    )


@router.delete("/{id}", response_description="user data deleted from the database")
async def delete_user_data(id: str):
    deleted_user = await delete_user(id)
    if deleted_user:
        return ResponseModel(
            "user with ID: {} removed".format(id), "user deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "user with id {0} doesn't exist".format(id)
    )