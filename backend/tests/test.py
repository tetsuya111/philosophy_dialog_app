import json

import requests

url="http://127.0.0.1:8000/api/auth/delete/"
user_url="http://127.0.0.1:8000/api/auth/user/me/"
register_url="http://127.0.0.1:8000/api/auth/register/"
login_url="http://127.0.0.1:8000/api/auth/login/"
delete_url="http://127.0.0.1:8000/api/auth/delete/"
#url="http://127.0.0.1:8000/api/auth/register/"
join_url="http://127.0.0.1:8000/api/matching/join/"
cancel_url="http://127.0.0.1:8000/api/matching/cancel/"

username="test18"
pw="test"

def register_test(session=requests):
    headers={
        "Content-Type":"application/json"
    }
    
    data={
        "username":username,
        "password":pw
    }

    res=session.post(register_url,headers=headers,data=json.dumps(data))
    return res
def login_test(session=requests):
    headers={
        "Content-Type":"application/json"
    }
    
    data={
        "username":username,
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

def delete_test(userid,session=requests):
    headers={
        "Content-Type":"application/json"
    }
    
    #url=f"{delete_url}{userid}/"
    url=delete_url

    res=session.delete(url,headers=headers)
    return res

def join_matching(session=requests):
    headers={
        "Content-Type":"application/json"
    }
    
    #url=f"{delete_url}{userid}/"
    res=session.get(join_url,headers=headers)
    return res

def cancel_matching(session=requests):
    headers={
        "Content-Type":"application/json"
    }
    
    #url=f"{delete_url}{userid}/"
    res=session.get(cancel_url,headers=headers)
    return res

session=requests.Session()

register_test(session)

login_test(session)

res=user_test(session) 
print(res.text)

res=join_matching(session)
print(res.text)

res=user_test(session) 
print(res.text)

