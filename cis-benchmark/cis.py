import json
import gspread
import time
import datetime


# service account key 파일 설정
sa_key_file = "[Key 파일 경로]"
gc = gspread.service_account(sa_key_file)

# 스프레드시트 설정
# 복사할 템플릿 정보
spreadsheetId = "[템플릿 사본의 스프레드시트 ID]"
sheetId = "[템플릿 사본의 "템플릿" 워크시트 ID]"
# 붙여넣기할 시트 정보
destSpreadsheetId = "[시트 ID]"

# 템플릿 복사
sheet = gc.open_by_key(spreadsheetId)
worksheet = sheet.get_worksheet_by_id(sheetId)
worksheet.copy_to(destSpreadsheetId)

# 생성된 워크시트의 title 설정
now = datetime.datetime.now()
month = now.month
sheetTitle = str(month) + "월"

# 생성된 워크시트의 이름과 인덱스 변경
newSheet = gc.open_by_key(destSpreadsheetId)
newWorksheet = newSheet.get_worksheet(-1)
newWorksheet.update_title(sheetTitle)
newWorksheet.update_index(0)

# CIS Benchmark 실행 결과 파싱
file = "[실행 결과 파일]"
with open(file, "rt", encoding='UTF-8') as f:
    data = json.load(f)
    
    # 1.IAM ~ 7.BigQuery의 7항목
    list = [0 for row in range(7)]

    for row in range(0, 7):
        list[row] = data["groups"][0]["groups"][row]["controls"]

    # 각종 결과 담을 리스트 선언
    title = []
    summary = []
    alarm = []
    ok = []
    info = []
    skip = []
    error = []
    item = []
    item_id = []
    item_title = []
    result = []
    
    for cnt in range(0, 7):
        # summary와 title 업데이트
        for i in list[cnt]:
            summary.append(i["summary"])
            title.append(i["title"])

        for i in summary:
            alarm.append(i["alarm"])
            ok.append(i["ok"])
            info.append(i["info"])
            skip.append(i["skip"])
            error.append(i["error"])
            
            # 결과(passed, failed, skipped) 판단
            if (i["ok"] > 0 and i["skip"] == 0 and i["alarm"] == 0 and i["info"] == 0 and i["error"] == 0):
                result.append("passed")
            elif (i["alarm"] > 0):
                result.append("failed")
            elif (i["error"] > 0):
                result.append("skipped")
            elif (i["info"] > 0 and i["alarm"] == 0 and i["ok"] == 0 and i["skip"] == 0 and i["error"] == 0):
                result.append("skipped")
            elif (i["alarm"] == 0 and ok == 0 and i["info"] == 0 and i["skip"] == 0 and i["error"] == 0):
                result.append("skipped")
            else: result.append("skipped")
    
        # 스프레드시트에 세부 상태 업데이트 
        newWorksheet.batch_update(
            [
                {
                    'range': 'E2',
                    'values': [alarm],
                    'majorDimension': 'COLUMNS'
                }
            ]
        )
        # gspread.exceptions.APIError: 'RATE_LIMIT_EXCEEDED' 방지를 위한 delay
        time.sleep(1.5)
        
        newWorksheet.batch_update(
            [
                {
                    'range': 'F2',
                    'values': [ok],
                    'majorDimension': 'COLUMNS'
                }
            ]
        )
        time.sleep(1.5)
        
        newWorksheet.batch_update(
            [
                {
                    'range': 'G2',
                    'values': [info],
                    'majorDimension': 'COLUMNS'
                }
            ]
        )
        time.sleep(1.5)
        
        newWorksheet.batch_update(
            [
                {
                    'range': 'H2',
                    'values': [skip],
                    'majorDimension': 'COLUMNS'
                }
            ]
        )
        time.sleep(1.5)
        
        newWorksheet.batch_update(
            [
                {
                    'range': 'I2',
                    'values': [error],
                    'majorDimension': 'COLUMNS'
                }
            ]
        )
        time.sleep(1.5)

        newWorksheet.batch_update(
            [
                {
                    'range': 'D2',
                    'values': [result],
                    'majorDimension': 'COLUMNS'
                }
            ]
        )
        time.sleep(1.5)

        summary.clear()
    
    # ID와 title(보안정책) 업데이트
    for i in title:
        item = i.split(' ', 1)
        item_id.append(item[0])
        item_title.append(item[1])

    newWorksheet.batch_update(
            [
                {
                    'range': 'A2',
                    'values': [item_id],
                    'majorDimension': 'COLUMNS'
                }
            ]
        )
    time.sleep(1.5)

    newWorksheet.batch_update(
        [
            {
                'range': 'B2',
                'values': [item_title],
                'majorDimension': 'COLUMNS'
            }
        ]
    )
    time.sleep(1.5)
