from django.shortcuts import render
import psycopg2
from django.http import HttpResponse
import json
from django.http import JsonResponse
from timeback.settings import *
from rest_framework.decorators import api_view
from django.db import Error
from datetime import datetime
import hashlib

#some shits 
def hashPassword(pass_word):
    password = pass_word
    hashObject = hashlib.sha256(password.encode())
    hashedPassword = hashObject.hexdigest()
    return hashedPassword


#services
@ api_view(['POST', "GET", "PUT", "PATCH", "DELETE"])
def getClient(request):
    action = 'getClient'
    jsond = json.loads(request.body)
    action = jsond.get('action', 'nokey')
    client_id = jsond.get('client_id', 'nokey')
    con = connect()
    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM timeorder.tbl_client WHERE timeorder.tbl_client.client_id = {client_id};")
    columns = cursor.description
    respRow = [{columns[index][0]: column.isoformat() if isinstance(column, datetime) else column for index,
                column in enumerate(value)} for value in cursor.fetchall()] 
    resp = sendResponse(200, "Амжилттай", respRow, action)
    return HttpResponse(resp)

@ api_view(['POST', "GET", "PUT", "PATCH", "DELETE"])
def getUser(request):
    action = 'getUser'
    jsond = json.loads(request.body)
    action = jsond.get('action', 'nokey')
    user_id = jsond.get('user_id', 'nokey')
    con = connect()
    cursor = con.cursor()
    cursor.execute(f"SELECT username, company_name, email, phone_number, picture FROM timeorder.tbl_user WHERE timeorder.tbl_user.user_id = {user_id}")
    columns = cursor.description
    respRow = [{columns[index][0]:column for index,
                column in enumerate(value)} for value in cursor.fetchall()]
    resp = sendResponse(200, "Амжилттай", respRow, action)
    return HttpResponse(resp)


@ api_view(['POST', "GET", "PUT", "PATCH", "DELETE"])
def createClient(request):
    action = 'createClient'
    try:
        data = json.loads(request.body)
        con = connect()
        cur = con.cursor()
        hashed_password = hashPassword(data['password'])
        created_at = datetime.now()
        cur.execute(
            """INSERT INTO timeorder.tbl_client 
               (first_name, last_name, username, password, email, phone_number, picture, created_at) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
               RETURNING client_id""",
            (data['first_name'], data['last_name'], data['username'], hashed_password, data['email'], data['phone_number'], data['picture'], created_at)
        )
        client_id = cur.fetchone()[0]
        con.commit()
        
        response_data = {
            "message": "Хэрэглэгч амжилттай бүртгэгдлээ.",
            "client_id": client_id
        }
        return JsonResponse(response_data, status=201)
    
    except Exception as error:
        response_data = {
            "error": str(error)
        }
        return JsonResponse(response_data, status=500)
    
    finally:
        if con is not None:
            con.close()