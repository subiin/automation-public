## **Metric Screenshot**

### 개요
- 목적
  * 모니터링 메트릭 스크린샷 생성 과정을 자동화하여 일관된 좌표의 이미지를 빠르게 생성합니다.

### 각 코드 설명
 - billing.py</br>
   변수를 적용한 Billing URL을 생성하여 화면을 띄운 후 스크린샷을 생성합니다.
    - 측정 월의 Billing 메트릭을 측정합니다.

   파일 실행 전 main 함수에서 아래의 변수 점검이 필요합니다.
     1. billing_id : 빌링 계정 ID
        project_id : 측정 대상 프로젝트의 ID 목록
        chrome_path : 크롬이 설치된 경로
     2. pyautogui.screenshot(today, region=(pos_X, pos_Y, width, height)) : 스크린샷을 생성할 좌표와 크기

   "billing_[project_id]_YYYY-mm.png" 형태로 이미지가 저장됩니다.</br></br>

- gce_all_cpu.py</br>
  VM CPU 사용률을 측정하는 Metric Explorer의 URL을 생성하여 화면을 띄운 후 스크린샷을 생성합니다.
    - 측정 월의 1일(오전 12시 00분)부터 말일(오후 11시 59분)까지의 메트릭을 측정합니다.
    - Aggregator : none, Aligner : max


  파일 실행 전 main 함수에서 아래의 변수 점검이 필요합니다.
    1. msp_project_id : 모니터링용 프로젝트가 생성되었다는 가정 하에 해당하는 Project ID
       instance_list : 측정 대상 VM 인스턴스의 이름 목록
       chrome_path : 크롬이 설치된 경로
    2. pyautogui.moveTo(pos_X, pos_Y) : 메트릭의 이름 범례를 나타내는 좌표
       pyautogui.screenshot(today, region=(pos_X, pos_Y, width, height)) : 스크린샷을 생성할 좌표와 크기

  "gce_cpu_util_YYYY-mm.png" 형태로 이미지가 저장됩니다.</br></br>

- gke_cpu.py</br>
  GKE CPU 사용률을 측정하는 Metric Explorer의 URL을 생성하여 화면을 띄운 후 스크린샷을 생성합니다.
    - 측정 월의 1일(오전 12시 00분)부터 말일(오후 11시 59분)까지의 메트릭을 측정합니다.
    - Aggregator : none, Aligner : max


  파일 실행 전 main 함수에서 아래의 변수 점검이 필요합니다.
    1. msp_project_id : 모니터링용 프로젝트가 생성되었다는 가정 하에 해당하는 Project ID
       instance_list : 측정 대상 VM 인스턴스(GKE)의 이름 목록
       chrome_path : 크롬이 설치된 경로
    2. pyautogui.moveTo(pos_X, pos_Y) : 메트릭의 이름 범례를 나타내는 좌표
       pyautogui.screenshot(today, region=(pos_X, pos_Y, width, height)) : 스크린샷을 생성할 좌표와 크기

  "gke_cpu_util_YYYY-mm.png" 형태로 이미지가 저장됩니다.</br></br>

  - cloud_sql.py
  Cloud SQL의 CPU/Memory/Disk 사용률을 측정하는 Metric Explorer의 URL을 생성하여 화면을 띄운 후 스크린샷을 생성합니다.
    - 측정 월의 1일(오전 12시 00분)부터 말일(오후 11시 59분)까지의 메트릭을 측정합니다.
    - Aggregator : none, Aligner : max

  파일 실행 전 main 함수에서 아래의 변수 점검이 필요합니다.
    1. msp_project_id : 모니터링용 프로젝트가 생성되었다는 가정 하에 해당하는 Project ID
       chrome_path : 크롬이 설치된 경로
    2. pyautogui.screenshot(today, region=(pos_X, pos_Y, width, height)) : 스크린샷을 생성할 좌표와 길이

  "sql_[metric]_YYYY-mm.png" 형태로 이미지가 저장됩니다.</br></br>

### 주의 및 제약 사항
  1. 사용된 파이썬 라이브러리(pyautogui)의 특성에 따라 파일을 실행시킬 때에는 반드시 화면이 필요합니다. 
     - 화면이 없이 스케줄링을 통한 자동 실행은 불가합니다.
  2. WSL 환경이 아닌 Windows에서 실행이 되어야 합니다.
  3. "pip install pyautogui"로 라이브러리 설치가 선행되어야 합니다.
  4. 해상도에 따라 스크린샷 위치가 달라지므로 좌표 확인이 필요합니다.
     - 파일에 작성된 좌표는 노트북 모델명: NT951XCJ(15.6인치), 해상도: 1920x1080, 앱의 배율: 125%를 기준으로 하였으며,
       샘플 이미지는 크롬 화면 배율이 billing.py: 80%, cpu_util.py, cloud_sql.py: 90%에서 캡처되었음을 참고 바랍니다.
     - print(pyautogui.position())로 마우스의 현재 좌표를 확인할 수 있습니다.
  5. 프로젝트 권한을 가지고 있는 계정이 크롬에 로그인되어 있어야 합니다.

