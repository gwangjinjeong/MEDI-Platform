from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
import hashlib
from collections import OrderedDict
import pandas as pd
import numpy as np

from algorithm import ml_models as algorithm

from server.database import ( # server의 database 폴더내 함수들 import
    add_user,
    add_bcm,
    add_physio,
    delete_user,
    retrieve_user,
    retrieve_users,
    retrieve_users_bcm,
    retrieve_users_physio,
    check_auth,
    update_user,
)
from server.models.user import ( # server의 models user폴더내 함수들 import
    ErrorResponseModel,
    ResponseModel,
    UserIn,
    UserOut,
    UserInDB,
    UserBCM,
    UserPhysio,
    UpdateUserModel,
)

router = APIRouter()

def secure_password_hasher(raw_password: str): # 문장을 hash함수로 암호화
    encoded_passwd = raw_password.encode()
    return hashlib.sha256(encoded_passwd).hexdigest()

def secure_save_user(user_in: UserIn): # 회원가입시 유저데이터 중에서 password만 암호화시키는 함수
    hashed_password = secure_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    return user_in_db

def save_readable_bcmdata(bcm_data: UserBCM): # 측정데이터가 16진수 데이터가 string으로 들어오는데 이를 사용자가 보기 편하게 바꿔주고 저장하는 함수
    fname = bcm_data['userid'] +'_'+ bcm_data['datetime']
    rawdata = bcm_data['bcmdata'].split('\n')[:-1]
    df_csv = pd.DataFrame(columns=['Time','685nm PD1(V)','685nm PD2(V)','685nm PD3(V)','785nm PD1(V)','785nm PD2(V)','785nm PD3(V)','830nm PD1(V)','830nm PD2(V)','830nm PD3(V)','850nm PD1(V)','850nm PD2(V)','850nm PD3(V)','9150nm PD1(V)','915nm PD2(V)','915nm PD3(V)','975nm PD1(V)','975nm PD2(V)','975nm PD3(V)'])
    for k, data in enumerate(rawdata):
        row_collection = [k] #k는 '초'
        v1 = data[1:].split('h')
        for each in v1:
            v2 = [int(each[i:i+4],16) for i in range(0, len(each), 4)]
            v3 = np.array(v2) * (1.65/32768) * np.array([bcm_data['gainPD1'],bcm_data['gainPD2'],bcm_data['gainPD3']])
            row_collection = row_collection + v3.tolist()
        df_csv.loc[k] = row_collection
    df_csv.to_csv(f'/workspace/MEDiPlatform/app/algorithm/data/raw_{fname}.csv', sep=',', na_rep='NaN',index=False)
    print('Saved! \nCongratulations!')
    return fname

@router.post("/", response_description="user data added into the database", response_model=UserOut) # 회원가입시 유저를 추가시키는 post 명령을 보낸다.
async def add_user_data(user: UserIn = Body(...)):
    user_secue = secure_save_user(user)
    user_json = jsonable_encoder(user_secue)
    new_user = await add_user(user_json)
    return new_user

@router.post("/bcm", response_description="user's raw bc data into the database",response_model=UserPhysio) # 측정데이터를 추가시키는 post 명령을 보낸다.
async def add_bcm_data(bcm: UserBCM = Body(...)):
    bcm_json = jsonable_encoder(bcm)
    new_bcm = await add_bcm(bcm_json)
    fname = save_readable_bcmdata(new_bcm)
    physio_data = algorithm.knn(fname)
    physio_data.to_csv(f'/workspace/MEDiPlatform/app/algorithm/data/physio_{fname}.csv', sep=',', na_rep='NaN',index=False)
    print('Saved! \nCongratulations!')
    physio_json = {'userid': new_bcm['userid']}
    physio_json['time'] = physio_data['time'].tolist()
    physio_json['mua685'] = physio_data['mua685nm'].tolist()
    physio_json['mua785'] = physio_data['mua785nm'].tolist()
    physio_json['mua830'] = physio_data['mua830nm'].tolist()
    physio_json['mua850'] = physio_data['mua850nm'].tolist()
    physio_json['mua915'] = physio_data['mua915nm'].tolist()
    physio_json['mua975'] = physio_data['mua975nm'].tolist()
    physio_json['mus685'] = physio_data['mus685nm'].tolist()
    physio_json['mus785'] = physio_data['mus785nm'].tolist()
    physio_json['mus830'] = physio_data['mus830nm'].tolist()
    physio_json['mus850'] = physio_data['mus850nm'].tolist()
    physio_json['mus915'] = physio_data['mus915nm'].tolist()
    physio_json['mus975'] = physio_data['mus975nm'].tolist()
    physio_json['hbo2'] = physio_data['HbO2'].tolist()
    physio_json['hhb'] = physio_data['HHb'].tolist()
    physio_json['water'] = physio_data['Water'].tolist()
    physio_json['fat'] = physio_data['Fat'].tolist()  
    physio_json = jsonable_encoder(physio_json)
    new_physio = await add_physio(physio_json)
    return new_physio

@router.get("/physio/{userid}", response_description="get user's bcm data") # 앱의 dashborad 진입시 유저의 분석데이터를 조회하는 명령을 보낸다.
async def get_users_physio(userid):
    users_physioall = await retrieve_users_physio(userid)
    if users_physioall:
        return ResponseModel(users_physioall,"physio data retrieved successfully")
    return  ResponseModel(users_physioall,"Empty list returned")

@router.get("/bcm/{userid}", response_description="get user's bcm data") # 앱의 유저의 측정데이터를 조회하는 명령을 보낸다.
async def get_users_bcm(userid):
    users_bcmall = await retrieve_users_bcm(userid)
    if users_bcmall:
        return ResponseModel(users_bcmall,"bcm data retrieved successfully")
    return  ResponseModel(users_bcmall,"Empty list returned")

@router.get("/", response_description="users retrieved") # 회원가입한 유저들의 목록을 조회하는 get명령을 보낸다.
async def get_users():
    users = await retrieve_users()
    if users:
        return ResponseModel(users, "users data retrieved successfully")
    return ResponseModel(users, "Empty list returned")


@router.get("/{id}", response_description="user data retrieved") # 특정 유저의 정보를 조회하는 get명령을 보낸다.
async def get_user_data(id):
    user = await retrieve_user(id)
    if user:
        return ResponseModel(user, "user data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "user doesn't exist.")
   
@router.get("/{id}/{password}", response_description="user_auth_check") # 로그인을 시도한 유저의 아이디와 비밀번호가 맞는지 확인하는 get 명령을 보낸다.
async def sign_check(id: str, password:str):
    hashed_password = secure_password_hasher(password)
    check_user = OrderedDict()
    check_user['userid'] = id
    check_user['hashed_password'] = hashed_password
    check_sign = await check_auth(check_user)
    if check_sign:
        return ResponseModel(check_sign, "Sign in successfully")
    return ErrorResponseModel("An error occurred.", 404, "wrong userid and password.")

@router.put("/{id}")     # 유저의 정보를 변경하는 put 명령을 보낸다.
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


@router.delete("/{id}", response_description="user data deleted from the database") # 유저데이터를 삭제하는 delete 명령을 보낸다.
async def delete_user_data(id: str):
    deleted_user = await delete_user(id)
    if deleted_user:
        return ResponseModel(
            "user with ID: {} removed".format(id), "user deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "user with id {0} doesn't exist".format(id)
    )

























































































































































































































































































































