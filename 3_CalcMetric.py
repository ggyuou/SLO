import sys
import configparser
import argparse
import datetime, time
import requests
import json
import sys
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

# SLO 생성을 위해 사용할 JSON 형태의 Body를 구성
def createJsonObj():
    requestBody = '''{
        "tsmMetricKey": "calc:service.myservices_fastreq_1000ms",
        "name": "myservices_fast_1000ms",
        "enabled": true,
        "metricDefinition": {
            "metric": "REQUEST_COUNT"
        },
        "unit": "COUNT",
		"managementZones": ["mzName"],
        "conditions": [
            {
                "attribute": "CPU_TIME",
                "comparisonInfo": {
                    "type": "NUMBER",
                    "comparison": "LOWER_THAN_OR_EQUAL",
                    "value": 1000,
                    "negate": false
                }
            }
        ],
        "dimensionDefinition": {
            "name": "Dimension",
            "dimension": "All requests",
            "topX": 10,
            "topXDirection": "DESCENDING",
            "topXAggregation": "SINGLE_VALUE"
        }
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
section = "calcm"
rstCondition = config.get(section, "rstCondition")

# 대상 Management Zone을 실행시 매개변수에서 받아옴
arg = sys.argv[1]
metricName = arg.replace(" ", "-")

# 매개변수에서 받은 Management Zone 이름을 JSON에 반영
calcName = "slo_fast_" + metricName + "_requests"
jsonObj = createJsonObj()
jsonObj["name"] = calcName
jsonObj["tsmMetricKey"] = "calc:service." + calcName
#jsonObj["filter"] = "type(\"SERVICE\"), mzName(\"" + arg + "\")"

# 매개변수에서 받은 Management Zone 이름을 JSON에 반영
#jsonObj["managementZones"][0] = "\"" + arg + "\""
jsonObj["managementZones"][0] = arg 

# 빠른 리퀘스트에 대한 응답 시간 조건을 환경 파일 값으로 부터 설정
jsonObj["conditions"][0]["comparisonInfo"]["value"] = rstCondition

#print(json.dumps(jsonObj))

apiUrl = "/api/config/v1/calculatedMetrics/service"
url, headers = createFullUrl(apiUrl, tenantID, APIToken)
response = requests.post(url, json=jsonObj, headers = headers)
if response.status_code == 201:
    print("== Success!")
else:
    print("== Failed!!!")
    print("-- 응답코드: %d" % response.status_code)
    print("-- 에러내용 --")
    print(response.text)
