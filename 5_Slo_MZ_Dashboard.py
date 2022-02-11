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

# SLO Dashboard 생성을 위해 사용할 JSON 형태의 Body를 구성
def createJsonObj():
    requestBody = '''{
		"dashboardMetadata": {
			"name": "PRD MS-LI_SLO_분석",
			"shared": false,
			"owner": "Dynatrace",
			"preset": true
		},
		"tiles": [
			{
				"name": "PRM MS-LI_성공율_분석",
				"tileType": "DATA_EXPLORER",
				"configured": true,
				"bounds": {
					"top": 0,
					"left": 0,
					"width": 494,
					"height": 418
				},
				"tileFilter": {
					"managementZone": {
						"id": "3485162005192694691",
						"name": "PRD MS-LI"
					}
				},
				"customName": "Data explorer results",
				"queries": [
					{
						"id": "A",
						"timeAggregation": "DEFAULT",
						"metricSelector": "(100)*(builtin:service.errors.fivexx.successCount:splitBy(\\\"dt.entity.service\\\"))/(builtin:service.requestCount.server:splitBy(\\\"dt.entity.service\\\"))",
						"splitBy": [],
						"enabled": true
					}
				],
				"visualConfig": {
					"type": "TABLE",
					"global": {
						"seriesType": "LINE",
						"hideLegend": false
					},
					"rules": [
						{
							"matcher": "A:",
							"properties": {
								"color": "DEFAULT"
							},
							"seriesOverrides": []
						}
					],
					"axes": {
						"xAxis": {
							"displayName": "",
							"visible": true
						},
						"yAxes": []
					},
					"heatmapSettings": {},
					"tableSettings": {
						"isThresholdBackgroundAppliedToCell": false
					},
					"graphChartSettings": {
						"connectNulls": false
					}
				}
			},
			{
				"name": "PRD MS-LI_CPU시간_분석",
				"tileType": "DATA_EXPLORER",
				"configured": true,
				"bounds": {
					"top": 0,
					"left": 494,
					"width": 494,
					"height": 418
				},
				"tileFilter": {
					"managementZone": {
						"id": "3485162005192694691",
						"name": "PRD MS-LI"
					}
				},
				"customName": "Data explorer results",
				"queries": [
					{
						"id": "A",
						"timeAggregation": "DEFAULT",
						"splitBy": [],
						"metricSelector": "(100)*(calc:service.slo_fast_PRD-MS-LI_requests:splitBy(\\\"dt.entity.service\\\"))/(builtin:service.requestCount.server:splitBy(\\\"dt.entity.service\\\"))",
						"enabled": true
					},
			        {
						"id": "B",
						"timeAggregation": "DEFAULT",
						"splitBy": [
							"dt.entity.service"
						],
						"metricSelector": "builtin:service.requestCount.server:splitBy(\"dt.entity.service\")",
						"enabled": true
					}
				],
				"visualConfig": {
					"type": "TABLE",
					"global": {
						"seriesType": "LINE",
						"hideLegend": false
					},
					"rules": [
						{
							"matcher": "A:",
							"properties": {
								"color": "DEFAULT"
							},
							"seriesOverrides": []
						},
						{
							"matcher": "B:",
							"properties": {
								"color": "DEFAULT"
							},
							"seriesOverrides": []
						}
					],
					"axes": {
						"xAxis": {
							"visible": true
						},
						"yAxes": []
					},
					"heatmapSettings": {},
			        "thresholds": [
						{
							"axisTarget": "LEFT",
							"columnId": "(100)*(calc:service.slo_fast_PRD-MS-LI_requests:splitBy(\\\"dt.entity.service\\\"))/(builtin:service.requestCount.server:splitBy(\\\"dt.entity.service\\\"))",
							"rules": [
								{
									"color": "#7dc540"
								},
								{
									"color": "#f5d30f"
								},
								{
									"color": "#dc172a"
								}
							],
							"queryId": "",
							"visible": true
						}
					],
					"tableSettings": {
						"isThresholdBackgroundAppliedToCell": false
					},
					"graphChartSettings": {
						"connectNulls": false
					}
				},
				"queriesSettings": {
					"resolution": ""
				}
			}
		]
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

# 대상 서비스 그룹을 실행시 매개변수에서 받아옴
arg = sys.argv[1]
metricName = arg.replace(" ", "-")

# Management Zone ID 가져오기
apiUrl = "/api/config/v1/managementZones"
r_json = dtapiget(apiUrl)
mzID = ""
for data in r_json["values"]:
	entityId = data["id"]
	entityName = data["name"]
	if arg == entityName:
		 mzID = entityId
if mzID == "":
	print("== Failed!!!")
	print('==manazement zone을 찾을 수 없습니다!!! %s' % arg)
	sys.exit()
#mzID = "3485162005192694691"

# 매개변수에서 받은 서비스 이름을 JSON에 반영
jsonObj = createJsonObj()
jsonObj["dashboardMetadata"]["name"] = arg + "_SLO_분석"
jsonObj["tiles"][0]["name"] = arg + "_성공율_분석"
jsonObj["tiles"][0]["tileFilter"]["managementZone"]["id"] = mzID
jsonObj["tiles"][0]["tileFilter"]["managementZone"]["name"] = arg
jsonObj["tiles"][1]["name"] = arg + "_응답시간_분석"
jsonObj["tiles"][1]["tileFilter"]["managementZone"]["id"] = mzID
jsonObj["tiles"][1]["tileFilter"]["managementZone"]["name"] = arg
jsonObj["tiles"][1]["queries"][0]["metricSelector"] = "(100)*((calc:service.slo_fast_" + metricName + "_requests:splitBy(\"dt.entity.service\"))/(builtin:service.requestCount.server:splitBy(\"dt.entity.service\")))"
jsonObj["tiles"][1]["visualConfig"]["thresholds"][0]["columnId"] = "(100)*((calc:service.slo_fast_" + metricName + "_requests:splitBy(\"dt.entity.service\"))/(builtin:service.requestCount.server:splitBy(\"dt.entity.service\")))"

# SLO dashboard 생성
apiUrl = "/api/config/v1/dashboards"
url, headers = createFullUrl(apiUrl, tenantID, APIToken)
response = requests.post(url, json=jsonObj, headers = headers)
if response.status_code == 201:
    print("== Success!")
else:
    print("== Failed!!!")
    print("-- 응답코드: %d" % response.status_code)
    print("-- 에러내용 --")
    print(response.text)
