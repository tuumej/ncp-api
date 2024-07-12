"""
생성자     : melca
생성일자   : 2024-07-08
설명      : 서버 백업

---

1. 서버 목록 조회
>> KVM / XEN 서버 구분

2. 서버 이미지 목록 조회

3. 서버 이미지 생성
> 규칙 : 서버명_YYMMDD
>>
기존 서버 이미지와 동일한 이름 필터링
4. 서버 이미지 삭제
> 규칙 : 
5. 결과 출력
> 삭제된 서버 이미지, 생성된 서버 이미지
>> 
실행 날자 : 24.07.01
[create]
(+) app_240701
(+) web_240701

[delete]
(-) app_230701
(-) web_230701

"""
import sys
import os
import hashlib
import hmac
import base64
import requests
import time
import json
import datetime

def commonFunc(lst):

    pList=lst

    timestamp = int(time.time() * 1000)
    timestamp = str(timestamp)
        
    access_key = "D6826154BFF47DE9775D"
    secret_key = "50BDD4517D5E8A72A7CDEAF48E01CE5AF1A3B793"
    secret_key = bytes(secret_key, 'UTF-8')
        
    api_server = "https://ncloud.apigw.ntruss.com"
    api_url = "/vserver/v2/" + pList[0]
    api_url = api_url + "?responseFormatType=json&regionCode=KR"
    #print(api_url)
    if len(pList) > 1:
        api_url = api_url + pList[1]

    method = "GET"

    message = method + " " + api_url + "\n" + timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
        
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
        
    http_header = {
        "x-ncp-apigw-signature-v2" : signingKey,
        "x-ncp-apigw-timestamp" : str(timestamp),
        "x-ncp-iam-access-key" : access_key,
    }

    return api_server+api_url, http_header

 # 1. 서버 목록 조회
def getServerInstanceList():
    pList=['getServerInstanceList']
    url, http_header=commonFunc(pList)

    server_response = requests.get(url, headers=http_header)
    data = json.loads(server_response.text)

    serverCnt = data['getServerInstanceListResponse']['totalRows']
    serverList = data['getServerInstanceListResponse']['serverInstanceList']
    # kvm, xen, etc 로 서버 하이퍼바이저 구분
    kvmServerList=[]
    xenServerList=[]
    etcServerList=[]

    for i in range(serverCnt):
        serverDict = {}
        serverDict['serverInstanceNo'] = serverList[i]['serverInstanceNo']
        serverDict['serverName'] = serverList[i]['serverName']
        serverDict['hypervisorType'] = serverList[i]['hypervisorType']['codeName']
        serverDict['serverInstanceStatus'] = serverList[i]['serverInstanceStatus']['code']

        # hypervisorType 구분 저장 (KVM/XEN/ETC)
        if serverDict['hypervisorType'] == "KVM":
            kvmServerList.append(serverDict)
        elif serverDict['hypervisorType'] == "XEN":
            xenServerList.append(serverDict)
        else:
            etcServerList.append(serverDict)

    #print("kvmServerList: ",kvmServerList)
    #print("xenServerList: ",xenServerList)
    #print("etcServerList: ",etcServerList)

    return kvmServerList, xenServerList, etcServerList

# 서버 이미지 목록 조회
def getMemberServerImageInstanceList():
    pList=['getMemberServerImageInstanceList']
    url, http_header=commonFunc(pList)

    server_response = requests.get(url, headers=http_header)
    data = json.loads(server_response.text)
    #print(data)

    sImgCnt = data['getMemberServerImageInstanceListResponse']['totalRows']
    sImgList = data['getMemberServerImageInstanceListResponse']['memberServerImageInstanceList']
    sImgListReq = []

    #print("sImgCnt : ",sImgCnt)

    for i in range(sImgCnt):
        sImgDict = {}
        sImgDict['memberServerImageInstanceNo'] = sImgList[i]['memberServerImageInstanceNo']
        sImgDict['memberServerImageName'] = sImgList[i]['memberServerImageName']
        sImgDict['originalServerInstanceNo'] = sImgList[i]['originalServerInstanceNo']
        #print(i," ",sImgDict['memberServerImageInstanceNo'],":",sImgDict['memberServerImageName'],":",sImgDict['originalServerInstanceNo'])

        sImgListReq.append(sImgDict)

    #print(sImgListReq)

    return sImgCnt, sImgListReq

# 블록 스토리지 스냅샷 인스턴스 리스트 조회
def getBlockStorageSnapshotInstanceList():
    pList=['getBlockStorageSnapshotInstanceList']
    url, http_header=commonFunc(pList)

    server_response = requests.get(url, headers=http_header)
    data = json.loads(server_response.text)
    #print(data)

    sImgCnt = data['getBlockStorageSnapshotInstanceListResponse']['totalRows']
    sImgList = data['getBlockStorageSnapshotInstanceListResponse']['blockStorageSnapshotInstanceList']
    sImgListReq = []

    #print("sImgCnt : ",sImgCnt)

    for i in range(sImgCnt):
        sImgDict = {}
        sImgDict['blockStorageSnapshotInstanceNo'] = sImgList[i]['blockStorageSnapshotInstanceNo']
        sImgDict['blockStorageSnapshotName'] = sImgList[i]['blockStorageSnapshotName']
        sImgDict['originalBlockStorageInstanceNo'] = sImgList[i]['originalBlockStorageInstanceNo']
        sImgDict['blockStorageSnapshotDescription'] = sImgList[i]['blockStorageSnapshotDescription']

        sImgListReq.append(sImgDict)
    
    print(sImgListReq)

# hypervisortype : XEN 인 서버 이미지 생성 
def createMemberServerImageInstance(sinfo, tdate):
    pUrl = "&serverInstanceNo=" + sinfo['serverInstanceNo']
    pUrl = pUrl + "&memberServerImageName=" + sinfo['serverName'] + "-" + tdate

    pList=['createMemberServerImageInstance', pUrl]
    url, http_header=commonFunc(pList)

    #print(pList)
    if sinfo['serverName'] == "c1-test-svr":
        print("url : ", url)
    #print("http_header : ",http_header)
    
    # 운영 중인 서버를 대상에서 제외하기 위한 조건
    if sinfo['serverName'] == "c1-test-svr":
        server_response = requests.get(url, headers=http_header)
        data = json.loads(server_response.text)
        print(data)

# hypervisortype : KVM 인 서버 이미지 생성
def createServerImage(sinfo, tdate):
    pUrl = "&serverInstanceNo=" + sinfo['serverInstanceNo']
    pUrl = pUrl + "&serverImageName=" + sinfo['serverName'] + "-" + tdate

    pList=['createServerImage', pUrl]
    url, http_header=commonFunc(pList)
    
    print(pList)
    print(url, http_header)

    server_response = requests.get(url, headers=http_header)
    data = json.loads(server_response.text)
    print(data)

# XEN 서버의 서버 이미지 삭제
def deleteMemberServerImageInstances(sinfo, sImgList):
    
    tSvrImgList=[]
    
    print("--------------------- Server Image List --------------------------------------------")
    for i in sImgList:
        print(i)
    print("------------------------------------------------------------------------------------")

    tSvrImgList=input("삭제할 인스턴스 번호 입력(,로 구분 ex. 1234,2344,2342) : ").replace(" ","").split(',')

    pUrl = ""

    for i in range(len(tSvrImgList)):
        pUrl = pUrl + "&memberServerImageInstanceNoList." + str(i+1) + "=" + tSvrImgList[i]

    pList=['deleteMemberServerImageInstances', pUrl]
    url, http_header=commonFunc(pList)
    
    #print(pUrl)
    #print(url, http_header)

    server_response = requests.get(url, headers=http_header)
    data = json.loads(server_response.text)
    print(data)


#def deleteBlockStorageSnapshotInstances():

def startServerInstances():
    # serverInstanceNoList.N
    tSvrList=[]
    
    print("--------------------- Server List --------------------------------------------")
    for i in sList:
        print(i)
    print("------------------------------------------------------------------------------")

    tSvrList=input("시작할 인스턴스 번호 입력(,로 구분 ex. 1234,2344,2342) : ").replace(" ","").split(',')

    print(tSvrList)

    pUrl = ""

    for i in range(len(tSvrList)):
        pUrl = pUrl + "&serverInstanceNoList." + str(i+1) + "=" + tSvrList[i]

    pList=['startServerInstances', pUrl]
    url, http_header=commonFunc(pList)

    server_response = requests.get(url, headers=http_header)
    data = json.loads(server_response.text)
    print(data)

def stopServerInstances(sList):
    # serverInstanceNoList.N
    tSvrList=[]
    
    print("--------------------- Server List --------------------------------------------")
    for i in sList:
        print(i)
    print("------------------------------------------------------------------------------")

    tSvrList=input("정지할 인스턴스 번호 입력(,로 구분 ex. 1234,2344,2342) : ").replace(" ","").split(',')

    print(tSvrList)

    pUrl = ""

    for i in range(len(tSvrList)):
        pUrl = pUrl + "&serverInstanceNoList." + str(i+1) + "=" + tSvrList[i]

    pList=['stopServerInstances', pUrl]
    url, http_header=commonFunc(pList)

    server_response = requests.get(url, headers=http_header)
    data = json.loads(server_response.text)
    print(data)


if __name__ == '__main__':

    now=datetime.datetime.now()
    fdate=now.strftime("%y%m%d")
    #print(fdate)

    fnum=99

    while fnum > 0 :
        print("-------------------------------")
        print("1. 서버 목록 조회")
        print("2. 서버 이미지 목록 조회")
        print("3. 서버 이미지 생성")
        print("4. 서버 이미지 삭제")
        print("5. 서버 시작")
        print("6. 서버 종료")
        print("-------------------------------")
        
        fnum=int(input("번호를 입력하세요.(-1 입력 시 종료) : "))

        if fnum==1:
            kvm, xen, etc=getServerInstanceList()
            print("하이퍼바이저 KVM 서버 목록")
            for i in kvm:
                print(i)
            print("하이퍼바이저 XEN 서버 목록")
            for i in xen:
                print(i)
        elif fnum==2:
            sImgCnt, sImgList=getMemberServerImageInstanceList()
            for i in sImgList:
                print(i)
        elif fnum==3:
            kvm, xen, etc=getServerInstanceList()

            if len(kvm) > 0:
                print("Create KVM Server Images!")
                #for i in kvm:
                    #createServerImage(i, fdate)
            # XEN 서버의 서버 이미지 생성
            if len(xen) > 0:
                print("Create XEN Server Images!")
                #for i in xen:
                    #createMemberServerImageInstance(i, fdate)
        elif fnum==4:
            # 4. 서버 이미지 삭제
            #  KVM 서버는 서버 이미지 생성될때 snapshot 이미지도 함께 생성됨. 삭제 로직 구현 시, 참고.

            # XEN 서버 이미지 삭제
            deleteMemberServerImageInstances(xen, sImgList)
        elif fnum==5:
            print("No 5")
        elif fnum==6:
            print("No 6")
            kvm, xen, etc=getServerInstanceList()
            stopServerInstances(kvm)

    
    

    