from django.shortcuts import render
import psycopg2
from django.http import HttpResponse
import json
from django.http import JsonResponse
from timeback.settings import *
from rest_framework.decorators import api_view
from django.db import Error
import datetime
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
    respRow = [{columns[index][0]:column for index,
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
def createClient(data,request):
    try:
        con = connect()
        cur = con.cursor()
        hashPassword()
        created_at = datetime.now()
        cur.execute(
            """INSERT INTO your_table_name 
               (first_name, last_name, username, password, email, phone_number, picture, created_at) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
               RETURNING client_id""",
            (data['first_name'], data['last_name'], data['username'], hashPassword, data['email'], data['phone_number'], data['picture'], created_at)
        )
        client_id = cur.fetchone()[0]
        resp = sendResponse(200, "Хэрэглэгч амжилттай бүртгэгдлээ.", "client_id": client_id, action)
        return HttpResponse(resp)
        con.commit()
    except Exception as error:
        return {"error": str(error)}, 500
    finally:
        if con is not None:
            con.close()