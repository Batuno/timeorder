from django.shortcuts import render
import psycopg2
from django.http import HttpResponse
import json
from django.http import JsonResponse
from timeback.settings import *
from rest_framework.decorators import api_view
from django.db import Error
import datetime

@ api_view(['POST', "GET", "PUT", "PATCH", "DELETE"])
def getClient(request):
    action = 'getClient'
    jsond = json.loads(request.body.decode('utf-8'))
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

