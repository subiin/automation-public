import pyautogui
import time
from datetime import datetime, timedelta
import calendar
import webbrowser

def calc_date(start_year, start_month):
    date = datetime(year=year, month=month, day=1).date()
    last_day = calendar.monthrange(date.year, date.month)[1]
    last_date = datetime(year=year, month=month, day=last_day).date()

    return last_date

def generate_instance_url(billing_id, year, month, project_id):
    last_day = calc_date(year, month)

    if(month < 10):
        month = "0" + str(month)

    instance_list_url = "https://console.cloud.google.com/billing/" + billing_id + "/reports;timeRange=CUSTOM_RANGE;from=" + str(year) + "-" + str(month) + "-01;to=" + str(last_day) + ";grouping=GROUP_BY_SERVICE;projects=" + project_id + "?cloudshell=false&orgonly=true&project=" + project_id + "&supportedpurview=organizationId"

    return instance_list_url

def open_browser(url, chrome_path):
    webbrowser.get(chrome_path + ' %s').open(url)                                       # if Chrome.exe is located at another path, change the directory path

if __name__ == '__main__':
    
    current_date = datetime.now()
    last_month = datetime(year=current_date.year, month=current_date.month, day=1) - timedelta(days=1)

    year        = last_month.year                                                                            # 연도 입력
    month       = last_month.month                                                                           # 월 입력                                                                         # 월 입력

    ## 1월 예외 처리
    start_year  = year
    start_month = month                                                                         

    if month == 1:
        start_month = 12
        start_year = year - 1

    ## set URL
    billing_id = "[Billing ID]"
    project_id = ["[Project ID1]", "[Project ID2]", ...]                                # Project ID 입력
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"               # Chrome 경로 입력

    for i in project_id:
        date_now = datetime.now()
        # "billing_[project_id]_YYYY-mm-dd.png" 형태로 이미지 저장
        today = "billing_" + i + ".png"
    
        ## open URL
        url = generate_instance_url(billing_id, year, month, i)
        open_browser(url, chrome_path)
        time.sleep(10)

        ## screenshot
        time.sleep(1)
        pyautogui.screenshot(today, region=(695, 310, 1220, 380))                           # 스크린샷용, 좌표 확인 
