import pyautogui
import time
from datetime import datetime, timedelta
import calendar
import webbrowser
    
def calc_date(year, month):
    date = datetime(year=year, month=month, day=1).date()
    last_day = calendar.monthrange(date.year, date.month)[1]
    last_date = datetime(year=year, month=month, day=last_day).date()
    
    return last_date

def generate_instance_url(start_date, last_date, msp_project_id):
    instance_list_url = "https://console.cloud.google.com/monitoring/metrics-explorer?cloudshell=false&orgonly=true&project=" + msp_project_id + "&supportedpurview=organizationId&pageState=%7B%22xyChart%22:%7B%22dataSets%22:%5B%7B%22timeSeriesFilter%22:%7B%22filter%22:%22metric.type%3D%5C%22compute.googleapis.com%2Finstance%2Fcpu%2Futilization%5C%22%20resource.type%3D%5C%22gce_instance%5C%22%22,%22minAlignmentPeriod%22:%2260s%22,%22aggregations%22:%5B%7B%22perSeriesAligner%22:%22ALIGN_MEAN%22,%22crossSeriesReducer%22:%22REDUCE_NONE%22,%22alignmentPeriod%22:%2260s%22,%22groupByFields%22:%5B%5D%7D,%7B%22crossSeriesReducer%22:%22REDUCE_NONE%22,%22alignmentPeriod%22:%2260s%22,%22groupByFields%22:%5B%5D%7D%5D%7D,%22targetAxis%22:%22Y1%22,%22plotType%22:%22LINE%22%7D%5D,%22options%22:%7B%22mode%22:%22COLOR%22%7D,%22constantLines%22:%5B%5D,%22timeshiftDuration%22:%220s%22,%22y1Axis%22:%7B%22label%22:%22y1Axis%22,%22scale%22:%22LINEAR%22%7D%7D,%22isAutoRefresh%22:true,%22timeSelection%22:%7B%22timeRange%22:%22custom%22,%22start%22:%22" + start_date + "T15:00:00.000Z%22,%22end%22:%22" + last_date + "T14:59:00.000Z%22%7D%7D"

    # for i in range(len(instance_list)):
    #     # instance가 2개 이상일 경우 Time series 추가
    #     if i != 0:
    #         instance_list_url = instance_list_url + ",%7B%22timeSeriesFilter%22:%7B%22filter%22:%22metric.type%3D%5C%22compute.googleapis.com%2Finstance%2Fcpu%2Futilization%5C%22%20resource.type%3D%5C%22gce_instance%5C%22%20metric.label.%5C%22instance_name%5C%22%3D%5C%22" + instance_list[i] + "%5C%22%22,%22minAlignmentPeriod%22:%2260s%22,%22aggregations%22:%5B%7B%22perSeriesAligner%22:%22ALIGN_MAX%22,%22crossSeriesReducer%22:%22REDUCE_NONE%22,%22alignmentPeriod%22:%2260s%22,%22groupByFields%22:%5B%5D%7D,%7B%22perSeriesAligner%22:%22ALIGN_NONE%22,%22crossSeriesReducer%22:%22REDUCE_NONE%22,%22alignmentPeriod%22:%2260s%22,%22groupByFields%22:%5B%5D%7D%5D%7D,%22targetAxis%22:%22Y1%22,%22plotType%22:%22LINE%22%7D"
            
    # instance_list_url = instance_list_url + "%5D,%22options%22:%7B%22mode%22:%22COLOR%22%7D,%22constantLines%22:%5B%7B%22label%22:%22%22,%22targetAxis%22:%22Y1%22,%22value%22:0.85%7D%5D,%22timeshiftDuration%22:%220s%22,%22y1Axis%22:%7B%22label%22:%22y1Axis%22,%22scale%22:%22LINEAR%22%7D%7D,%22isAutoRefresh%22:true,%22timeSelection%22:%7B%22timeRange%22:%22custom%22,%22start%22:%22" + start_date + "T15:00:00.000Z%22,%22end%22:%22" + last_date + "T14:59:00.000Z%22%7D%7D&project=" + msp_project_id + "&cloudshell=false&orgonly=true&supportedpurview=organizationId"

    return instance_list_url

def open_browser(url, chrome_path):
    webbrowser.get(chrome_path + ' %s').open(url)

if __name__ == '__main__':
    ## set Custom Date
    current_date = datetime.now()
    last_month = datetime(year=current_date.year, month=current_date.month, day=1) - timedelta(days=1)
    

    year        = last_month.year                                                                            # 연도 입력 
    month       = last_month.month                                                                           # 월 입력 
    
    ## 1월 예외 처리
    start_year  = year
    start_month = month                                                                         

    if month != 1:
        start_month = month-1
        start_year = year
    else:
        start_month = 12
        start_year = year-1

    ## set URL
    msp_project_id = "[Project ID]"                                                     # MSP Project ID 입력 
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"               # Chrome 경로 입력 

    ## set Date & File Name
    start_date = str(calc_date(start_year, start_month))
    last_date = str(calc_date(year, month))
    date_now = datetime.now()

    # "gce_cpu_YYYY-mm.png" 형태로 이미지 저장
    today = "bq_stored_bytes_{}{:>02d}.png".format(last_month.year, last_month.month)
    
    ## open URL
    url = generate_instance_url(start_date, last_date, msp_project_id)
    open_browser(url, chrome_path)
    time.sleep(10)

    ## set chrome window to 80%
    pyautogui.hotkey('ctrl','0')
    pyautogui.hotkey('ctrl','-')
    pyautogui.hotkey('ctrl','-')
    time.sleep(2)

    ## screenshot
    pyautogui.moveTo(520, 380)                                                          # 범례 나타내기용, 좌표 확인 
    time.sleep(5)
    
    pyautogui.screenshot(today, region=(695, 310, 1220, 380)) 