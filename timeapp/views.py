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

#hashpassword 
def hashPassword(pass_word):
    password = pass_word
    hashObject = hashlib.sha256(password.encode())
    hashedPassword = hashObject.hexdigest()
    return hashedPassword


#services
def getClient(request):
    try:
        action = 'getClient'
        jsond = json.loads(request.body)
        client_id = jsond.get('client_id', 'nokey')
        con = connect()
        cursor = con.cursor()
        cursor.execute(f"SELECT * FROM timeorder.tbl_client WHERE timeorder.tbl_client.client_id = {client_id};")
        columns = cursor.description
        respRow = [{columns[index][0]: column.isoformat() if isinstance(column, datetime) else column for index,
                    column in enumerate(value)} for value in cursor.fetchall()] 
        if not respRow:
            response_data = {
                "message": "Хэрэглэгчийн id тай тохирсон хэрэглэгч олдсонгүй."
            }
            return JsonResponse(response_data, status=404)
        response_data = {
            "message": "Амжилттай",
            "respRow": respRow,
            "action": action
        }
        return JsonResponse(response_data, status=200)
    except Exception as error:
        response_data = {
            "error": str(error),
            "message": "Бүртгэлтэй хэрэглэгч олдсонгүй."
        }
        return JsonResponse(response_data, status=500)
    
    finally:
        if con is not None:
            con.close()



def getUser(request):
    try:
        action = 'getUser'
        jsond = json.loads(request.body)
        user_id = jsond.get('user_id', 'nokey')
        con = connect()
        cursor = con.cursor()
        cursor.execute(f"SELECT username, company_name, email, phone_number, picture FROM timeorder.tbl_user WHERE timeorder.tbl_user.user_id = %s ", [user_id])
        columns = cursor.description
        respRow = [{columns[index][0]:column for index,
                    column in enumerate(value)} for value in cursor.fetchall()]
        if not respRow:
            response_data = {
                "message": "Хэрэглэгчийн id тай тохирсон хэрэглэгч олдсонгүй."
            }
            return JsonResponse(response_data, status=404)
        response_data = {
            "message": "Амжилттай",
            "respRow": respRow,
            "action": action
        }
        return JsonResponse(response_data, status=200)
    except Exception as error:
        response_data = {
            "error": str(error),
            "message": "Бүртгэлтэй хэрэглэгч олдсонгүй."
        }
        return JsonResponse(response_data, status=500)
    
    finally:
        if con is not None:
            con.close()


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
            "error": str(error),
            "message": "Хэрэглэгч бүртгэхэд алдаа гарлаа."

        }
        return JsonResponse(response_data, status=500)
    
    finally:
        if con is not None:
            con.close()


def loginClient(request):
    try:
        jsond = json.loads(request.body)
        username = jsond.get('username', 'nokey')
        email = jsond.get('email', 'noemail')
        password = jsond.get('password', '')
        con = connect()
        cur = con.cursor()
        hashed_password = hashPassword(password)
        cur.execute(f"""
                    SELECT client_id, username, email, password FROM timeorder.tbl_client WHERE username = %s OR email = %s""",
                    [username, email]
                    )
        user_data = cur.fetchone()

        if user_data and hashed_password == user_data[3]:
            response_data = {
                "client_id":user_data[0],
                "username":user_data[1],
                "email":user_data[2],
                "message": "Амжилттай нэвтэрлээ."
            }
            return JsonResponse(response_data, status=200)
        else:
            response_data = {
                "message": "Хэрэглэгчийн нэр эсвэл нууц үг буруу байна"
            }
            return JsonResponse(response_data, status=401)


    except Exception as error:
        error_message = str(error)
        response_data = {
            "error": error_message,
            "message": "Амжилтгүй оролдлого."
        }
        return JsonResponse(response_data, status=500)
    finally:
        if con is not None:
            con.close()

def createUser(request):
    try:
        data = json.loads(request.body)
        con = connect()
        cur = con.cursor()
        hashed_password = hashPassword(data['password'])
        created_at = datetime.now()
        cur.execute(
            """INSERT INTO timeorder.tbl_user as u
            (username, password, company_name, email, phone_number, picture, client_id, status_id, created_at)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *""",
            (data['username'], hashed_password, data['company_name'], data['email'], data['phone_number'], data['picture'], data['client_id'],data['status_id'], created_at)
        )
        user_id = cur.fetchone()
        con.commit()
        response_data = {
            "message": "Хэрэглэгч амжилттай бүртгэгдлээ.",
            "user_id": user_id
        }
        return JsonResponse(response_data, status=201)


    except Exception as error:
        response_data = {
            "error": str(error),
            "message": "Хэрэглэгч бүртгэхэд алдаа гарлаа."

        }
        return JsonResponse(response_data, status=500)
    finally:
        if con is not None:
            con.close()


def loginUser(request):
    try:
        jsond = json.loads(request.body)
        username = jsond.get('username', 'nokey')
        email = jsond.get('email', 'noemail')
        password = jsond.get('password', '')
        con = connect()
        cur = con.cursor()
        hashed_password = hashPassword(password)
        cur.execute(f"""
                    SELECT user_id, username, email, password FROM timeorder.tbl_user u WHERE username = %s OR email = %s""",
                    [username, email]
                    )
        user_data = cur.fetchone()

        if user_data and hashed_password == user_data[3]:
            response_data = {
                "user_id":user_data[0],
                "username":user_data[1],
                "email":user_data[2],
                "message": "Амжилттай нэвтэрлээ."
            }
            return JsonResponse(response_data, status=200)
        else:
            response_data = {
                "message": "Хэрэглэгчийн нэр эсвэл нууц үг буруу байна"
            }
            return JsonResponse(response_data, status=401)


    except Exception as error:
        error_message = str(error)
        response_data = {
            "error": error_message,
            "message": "Амжилтгүй оролдлого."
        }
        return JsonResponse(response_data, status=500)
    finally:
        if con is not None:
            con.close()