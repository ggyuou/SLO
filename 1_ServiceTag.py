import argparse
import configparser
import datetime
import json
import sys
import time

import requests
from requests import api
from requests.api import request


# 완성된 Full Url과 header를 생성해 줌
def createFullUrl(apiUrl, tenantID, APIToken):
    if "/e/" in tenantID:
        url = tenantID + apiUrl
        if not url.startswith("https://"):
            url = "https://" + url
    else:
        url = f"https://{tenantID}.live.dynatrace.com" + apiUrl
    headers = {'accept': "application/json", "Authorization": "Api-Token " + APIToken}
    return url, headers

# 해당 API Url을 이용해 GET 방식으로 호출한 후 결과를 반환
def dtapiget(apiUrl):
    global tenantID
    global APIToken
    url, headers = createFullUrl(apiUrl, tenantID, APIToken)
    response = requests.get(url, headers = headers)
    r_json = response.json()
    return r_json

# Tag 생성을 위해 사용할 JSON 형태의 Body를 구성
def createJsonObj():
    requestBody = '''{
        "name": "Book services",
        "description": null,
        "rules": [
            {
                "type": "SERVICE",
                "enabled": true,
                "valueFormat": null,
                "propagationTypes": [],
                "conditions": [
                    {
                        "key": {
                            "attribute": "SERVICE_NAME",
                            "type": "STATIC"
                        },
                        "comparisonInfo": {
                            "type": "STRING",
                            "operator": "CONTAINS",
                            "value": "book",
                            "negate": false,
                            "caseSensitive": false
                        }
                    }
                ]
            }
        ],  
        "entitySelectorBasedRules": []
    }'''
    jsonObj = json.loads(requestBody)
    return jsonObj

################################################ 메인 작업 수행 ###############################################

# 대상 환경(Tenant or Environment) 정보를 설정 파일에서 가져옴
config = configparser.RawConfigParser()
config.read('./dtenv.properties', encoding='utf-8')
section = "tenant"
tenantID = config.get(section, "tenantID")
APIToken = config.get(section, "APIToken")

# 태깅 하려는 대상 서비스 이름을 실행시 매개변수에서 받아옴
arg = sys.argv[1]

# 매개변수에서 받은 서비스 이름을 JSON에 반영
jsonObj = createJsonObj()
jsonObj["name"] = arg + " services"
jsonObj["rules"][0]["conditions"][0]["comparisonInfo"]["value"] = arg

print("=====================================================================================================")
print("                               %s services Tag 생성" % arg)
print("=====================================================================================================")
apiUrl = "/api/config/v1/autoTags"
url, headers = createFullUrl(apiUrl, tenantID, APIToken)
response = requests.post(url, json=jsonObj, headers = headers)
if response.status_code == 201:
    print("== Success!")
else:
    print("== Failed!!!")
    print("-- 응답코드: %d" % response.status_code)
    print("-- 에러내용 --")
    print(response.text)
