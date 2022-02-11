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
      "enabled": true,
      "name": "my services 성공율",
	  "metricExpression":"(100)*(builtin:service.errors.fivexx.successCount:splitBy())/(builtin:service.requestCount.server:splitBy())",
      "useRateMetric": true,
      "metricRate": "",
      "metricNumerator": "",
      "metricDenominator": "",
      "evaluationType": "AGGREGATE",
      "filter": "" ,
      "target": 95,
      "warning": 98,
      "timeframe": "-1d"
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

# SLO 생성을 위해 사용할 JSON 형태의 Body를 구성하고 사용자 정의 값 할당
section = "slo"
target = config.get(section, "target")
warning = config.get(section, "warning")
timeframe = config.get(section, "timeframe")

# 대상 서비스 그룹을 실행시 매개변수에서 받아옴
arg = sys.argv[1]

# 매개변수에서 받은 서비스 이름을 JSON에 반영
jsonObj = createJsonObj()
jsonObj["name"] = arg + " services 성공율"
#jsonObj["filter"] = "type(\\\"SERVICE\\\"), mzName(\"" + arg + "\")"
jsonObj["filter"] = "type(\"SERVICE\"), mzName(\"" + arg + "\")"

# 환경 파일의 설정을 JSON에 반영
jsonObj["target"] = target
jsonObj["warning"] = warning
jsonObj["timeframe"] = timeframe

apiUrl = "/api/v2/slo"
url, headers = createFullUrl(apiUrl, tenantID, APIToken)
response = requests.post(url, json=jsonObj, headers = headers)
if response.status_code == 201:
    print("== Success!")
else:
    print("== Failed!!!")
    print("-- 응답코드: %d" % response.status_code)
    print("-- 에러내용 --")
    print(response.text)
