from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
import hashlib
from collections import OrderedDict

from server.database import (
    add_user,
    add_bcm,
    delete_user,
    retrieve_user,
    retrieve_users,
    check_auth,
    # duplicate_check,
    update_user,
)
from server.models.user import (
    ErrorResponseModel,
    ResponseModel,
    UserIn,
    UserOut,
    UserInDB,
    UserBCM,
    UpdateUserModel,
)

router = APIRouter()

def secure_password_hasher(raw_password: str):
    encoded_passwd = raw_password.encode()
    return hashlib.sha256(encoded_passwd).hexdigest()

def secure_save_user(user_in: UserIn):
    hashed_password = secure_password_hasher(user_in.password)
    # print(hashed_password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    return user_in_db

@router.post("/", response_description="user data added into the database", response_model=UserOut)
async def add_user_data(user: UserIn = Body(...)):
    user_secue = secure_save_user(user)
    user_json = jsonable_encoder(user_secue)
    new_user = await add_user(user_json)
    return new_user

@router.post("/bcm/", response_description="user's raw bc data into the database",response_model=UserBCM)
async def add_bcm_data(bcm: UserBCM = Body(...)):
    bcm_json = jsonable_encoder(bcm)
    print('router bcm_json:'+bcm_json)
    new_bcm = await add_bcm(bcm_json)
    print('new bcm_json:'+new_bcm)
    return new_bcm

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

# @router.get("/{id}", response_description="Check the duplicated_userid")
# async def duplicate_id_check(id: str):
#     print(id)
#     duChek = await duplicate_check(id)
#     if duChek:
#         return ResponseModel(duChek, "user data retrieved successfully")
#     return ErrorResponseModel("An error occurred.", 404, "user doesn't exist.")
    
@router.get("/{id}/{password}", response_description="user_auth_check")
async def sign_check(id: str, password:str):
    hashed_password = secure_password_hasher(password)
    check_user = OrderedDict()
    check_user['userid'] = id
    check_user['hashed_password'] = hashed_password
    check_sign = await check_auth(check_user)
    if check_sign:
        return ResponseModel(check_sign, "Sign in successfully")
    return ErrorResponseModel("An error occurred.", 404, "wrong userid and password.")

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