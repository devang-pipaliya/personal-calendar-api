# import os
# import requests
# import traceback
#
# from fastapi import Security, HTTPException
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from app.entity.recruiter import RecruiterProfile
#
#
# token_type = HTTPBearer()
#
# def auth_wrapper(auth: HTTPAuthorizationCredentials = Security(token_type)):
#     # try: TODO remove comments when all things work fine
#     # try:
#     # import wdb
#     # wdb.set_trace()
#     print(f"Inside auth_wrapper")
#     url = f"{os.environ.get('IAM_API_SERVER_URL')}/user/validate-token"
#     headers = {
#         "customer_secret_key": f"{os.environ.get('IAM_CUSTOMER_SECRET_KEY')}",
#         "app_identifier": f"{os.environ.get('IAM_APP_IDENTIFIER')}",
#         "Authorization": f"Bearer {auth.credentials}"
#     }
#     response = requests.get(url, headers=headers)
#     print(f"\n########## response \n{response}")
#     response_data = response.json()
#     print(f"\n########## response.json \n{response_data}")
#     if response.status_code !=200:
#         raise HTTPException(status_code=response.status_code, detail=response_data.get("message", ""))
#     elif response_data.get("data", {}).get("is_valid"):
#         # response = response.json()
#         print(f"response_data -> {response_data}")
#         user = response_data["data"]["user"]
#         query = {"iam_user_id": user.get("id")}
#         print(f"query-> {query}")
#         recruiter = RecruiterProfile().get_single_record(query)
#         print(f"recruiter --> {recruiter}")
#         if recruiter:
#             return recruiter
#         raise HTTPException(status_code=400, detail="Record not Found")
#     else:
#         raise HTTPException(status_code=response.status_code, detail=response_data.get("message", ""))
#     # except Exception as exc:
#     #     print(f"exc-> {exc}")
#     #     traceback.print_exc()
#     #     raise exc
