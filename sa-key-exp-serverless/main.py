import os
import functions_framework
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from datetime import datetime, timedelta
import requests
from flask import Flask, request, jsonify

project_name = os.getenv('PROJECT_NAME', 'projects/[PROJECT_NAME]')
webhook_url = os.getenv('WEBHOOK_URL', '[SLACK_WEBHOOK_URL]')

credentials = GoogleCredentials.get_application_default()
service = discovery.build('iam', 'v1', credentials=credentials)
left_days = 7

# GCP 프로젝트 내 모든 Service Account를 리스팅
def count_function():
  request = service.projects().serviceAccounts().list(name=project_name)
  # Service Account를 담는 리스트
  sa_list = []

  # 이메일 형태(ex: @project-name.iam.gserviceaccount.com)의 Service Account를 리스트에 저장
  # 참고 : https://cloud.google.com/iam/docs/reference/rest/v1/projects.serviceAccounts/list#python
  while True:
    response = request.execute()
    for sa in response.get('accounts', []):
      sa_list.append(sa['email'])
    request = service.projects().serviceAccounts().list_next(previous_request=request, previous_response=response)
    if request is None:
      break

  return sa_list

# HTTP 요청
@functions_framework.http
# 현재 시간으로부터 +7일 이내에 만료되는 Service Account key 정보를 리스팅
def get_sa_key(request):
  sa_list = count_function()
  # 만료 예정인 Service Account를 저장
  result = []

  # 만료 예정인 Service Account key 찾기
  for sa in sa_list:
    saname = project_name + '/serviceAccounts/' + sa
    request = service.projects().serviceAccounts().keys().list(name=saname)
    response = request.execute()
    temp = response['keys']

    # keyType이 USER_MANAGED인 Service Account key의 만료 시간 계산
    for i in temp:
      if i['keyType'] == 'USER_MANAGED':
        sa_valid_before_time = i['validBeforeTime']
        sa_formatted_time = datetime.strptime(sa_valid_before_time.replace("T", " ")[:19], '%Y-%m-%d %H:%M:%S')
        now = datetime.now()

        # 현재 시간 기준 +7일 이내 만료되는 Service Account key를 result 리스트에 저장
        if abs(sa_formatted_time - now) < timedelta(days=left_days):
          result.append({
            'name': i['name'].split('/')[3],
            'key_name': i['name'].split('/')[5],
            'sa_string_time': sa_formatted_time.strftime('%Y-%m-%d %H:%M:%S')
          })

  return result

# Slack에 메시지 전달
def notify_slack(message):
  slack_data = {'text': message}
  response = requests.post(webhook_url, json=slack_data, headers={'Content-Type': 'application/json'})

  # 에러 발생 알림
  if response.status_code != 200:
    raise ValueError(f'Slack error 발생 ({response.status_code})\n response:\n{response.text}')

@functions_framework.http
def main(request):
  # get_sa_key(request) 호출하여 만료 예정 key 정보 저장
  expiring_keys = get_sa_key(request)

  # 만료 예정 key가 있을 경우 Service Account 이름, Service Account key 이름, 만료 시간 안내
  if expiring_keys:
    message = "Service account 키 만료 알람\n============================\n"
    for key in expiring_keys:
      message += f"- {key['name']}가 {key['sa_string_time']}에 만료됩니다.\n"
    message += f"  ({key['key_name']})\n\n"
    notify_slack(message)
  else:
    notify_slack("만료 예정인 Service account 키가 없습니다.")
  return "Notification sent to Slack"

# main 함수 실행
if __name__ == "__main__":
    app = Flask(__name__)

    @app.route("/", methods=["POST"])
    def handle_request():
        return main(request)

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))