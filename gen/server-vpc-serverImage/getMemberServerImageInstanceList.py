"""
생성자      : melca
생성일자    : 2023-09-14
설명        : 서버 인스턴스 목록 조회
"""

import hashlib
import hmac
import base64
import requests
import json
import time
from datetime import datetime

import configparser

config = configparser.ConfigParser()
config.read('/home/ncptest/ncp-api/config.ini')

# init
timestamp = int(time.time() * 1000) 

# api info
access_key = config['DEFAULT']['ACCESS_KEY']
secret_key = config['DEFAULT']['SECRET_KEY']
secret_key = bytes(secret_key, "UTF-8")

api_server = "https://ncloud.apigw.ntruss.com"

api_url = "/vserver/v2/getServerInstanceList"
api_url = api_url + "?responseFormatType=json&regionCode=KR"
api_url = api_url + "&serverInstanceStatusCode=NSTOP"  # Options : INIT | CREAT | RUN | NSTOP

api_method = "GET"

#print(api_url)

# message info
message = api_method + " " + api_url + "\n" + str(timestamp) + "\n" + access_key
message = bytes(message, "UTF-8")

signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

# http header
http_header = {
  "x-ncp-apigw-signature-v2" : signingKey,
  "x-ncp-apigw-timestamp" : str(timestamp),
  "x-ncp-iam-access-key" : access_key,
}

# call
server_response = requests.get(api_server + api_url, headers=http_header)
data = json.loads(server_response.text)
#print(data)

### data에서 각 서버의 serverInstanceNo, serverName 만 추출

serverCnt = data['getServerInstanceListResponse']['totalRows']
serverList = data['getServerInstanceListResponse']['serverInstanceList']
svrImgList = []

#print(serverCnt)
#print(serverList)

for i in range(serverCnt):
  svrImgdict = {}
  svrImgdict['serverInstanceNo'] = serverList[i]['serverInstanceNo']
  svrImgdict['serverName'] = serverList[i]['serverName']
  svrImgList.append(svrImgdict)

print(svrImgList)
