import json

import requests

url="http://127.0.0.1:8000/api/auth/delete/"
user_url="http://127.0.0.1:8000/api/auth/user/me/"
login_url="http://127.0.0.1:8000/api/auth/login/"
delete_url="http://127.0.0.1:8000/api/auth/delete/"
#url="http://127.0.0.1:8000/api/auth/register/"


def login_test(session=requests):
    headers={
        "Content-Type":"application/json"
    }

    pw="test"
    data={
        "username":"test5",
        "password":pw
    }

    res=session.post(login_url,headers=headers,data=json.dumps(data))
    return res

def user_test(session=requests):
    headers={
        "Content-Type":"application/json"
    }

    res=session.get(user_url,headers=headers)
    return res

def delete_test(session=requests):
    headers={
        "Content-Type":"application/json"
    }
    
    res=session.delete(delete_url,headers=headers)
    return res

session=requests.Session()
login_test(session)

delete_test(session)
