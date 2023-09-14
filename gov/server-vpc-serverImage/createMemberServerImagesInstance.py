"""
생성자      : melca
생성일자    : 2023-09-14
설명        : 서버 이미지 생성 (공공기관용)
"""

import hashlib
import hmac
import base64
import requests
import json
import time
from datetime import datetime

from getMemberServerImageInstanceList import *

import configparser

config = configparser.ConfigParser()
config.read('/home/ncptest/ncp-api/config.ini')

# init
timestamp = int(time.time() * 1000) 
now = datetime.now()

# api info
access_key = config['DEFAULT']['ACCESS_KEY']
secret_key = config['DEFAULT']['SECRET_KEY']
secret_key = bytes(secret_key, "UTF-8")

api_server = "https://ncloud.apigw.gov-ntruss.com"

api_url = "/vserver/v2/createMemberServerImageInstance"

### getMemberServerImageInstanceList.py에서 전달받은 svrImgList변수에 저장된 서버의 이미지 생성

for i in range(serverCnt):
    api_url_param = "?responseFormatType=json&regionCode=KR"
    api_url_param = api_url_param + "&serverInstanceNo=" + svrImgList[i]['serverInstanceNo']
    api_url_param = api_url_param + "&memberServerImageName=" +  svrImgList[i]['serverName'] 
    api_url_param = api_url_param + "-" + str(now.year) + "-" + str(now.month)

    api_method = "GET"

    print(api_url_param)

    # message info
    message = api_method + " " + api_url + api_url_param + "\n" + str(timestamp) + "\n" + access_key
    message = bytes(message, "UTF-8")

    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

    # http header
    http_header = {
      "x-ncp-apigw-signature-v2" : signingKey,
      "x-ncp-apigw-timestamp" : str(timestamp),
      "x-ncp-iam-access-key" : access_key,
    }


    # call
    server_response = requests.get(api_server + api_url + api_url_param, headers=http_header)
    data = json.loads(server_response.text)
    print(data)

