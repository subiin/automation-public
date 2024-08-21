## **CIS Benchmark 결과 취합 자동화**

### 개요
- 목적
  * CIS Benchmark 결과를 시트에 수동으로 작성하던 불편함을 줄입니다.
- 파일 설명
  * CIS Benchmark를 수행하여 생성된 json 형태의 결과 파일을 파싱하여 항목 ID와 그 결과를 스프레드시트에 자동으로 업데이트합니다.
    * cis.py : 자동화를 수행하는 메인 파일

### 사용 서비스
- CIS Benchmark - Steampipe(https://github.com/turbot/steampipe)
  * 기존의 inspec-gcp-cis-benchmark는 버전 문제로 인하여 steampipe로 변경하였습니다.
- Google Spreadsheet
- GCP IAM - Service Account
  * key 파일(Viewer 권한) 필요

### Pre-requisites
- 스프레드시트에 write하기 위해 필요한 gspread 모듈 설치를 위해 로컬 환경에서 "pip3 install gspread"를 실행합니다.
- "Viewer" 권한을 가진 GCP 서비스 계정을 생성하여 json 키 파일을 생성합니다.
- 자동화를 수행할 스프레드시트에서 GCP 서비스 계정에 "편집자" 권한을 부여하여 워크시트를 업데이트하도록 합니다.
  * 스프레드시트 우측 상단 "공유" 버튼 클릭 > 서비스 계정 입력 > "편집자" 권한 부여
- CIS Benchmark를 수행하여 수행 결과 파일을 로컬 PC에 다운로드합니다.
  * html, csv가 아닌 json 파일이 생성되도록 합니다.

### 실행 방법

1. 수행 결과 파일을 로컬 PC에 다운로드합니다.
2. cis.py에 정보를 입력합니다.
 * sa_key_file : Key 파일 경로
 * spreadsheetId : 템플릿 스프레드시트 사본의 스프레드시트 ID
 * sheetId : 템플릿 스프레드시트 사본의 "템플릿" 워크시트 ID
 * destSpreadsheetId : 결과 취합 스프레드시트 ID
 * file : 수행 결과 파일 경로
3. cis.py를 실행합니다.
 * 템플릿 워크시트가 결과 취합 스프레드시트에 복사되며, 해당 워크시트에 json 수행 결과 파일에서 파싱된 값이 자동으로 업데이트됩니다.

### 주의 및 제약 사항
- cis.py에 수정사항이 생겨 업데이트를 할 경우 Source Repositories에 서비스 계정 키 파일이 업로드되지 않도록 주의합니다.
- gspread.exceptions.APIError: 'RATE_LIMIT_EXCEEDED' 에러가 발생하지 않도록 sleep 함수를 유지해야 합니다.
  * 1 User 당 1분에 스프레드시트에 write할 수 있는 개수는 기본 60개이므로, 에러가 발생하지 않는 선에서 delay를 조정 가능합니다.
- D열 ~ H열은 steampipe의 세부 결과이므로, 나타내고 싶지 않으면 열 숨기기를 합니다.
- C열에 B열의 문자열 번역 함수(GOOGLETRANSLATE())가 적용되어 있으므로 C열 내 셀이 다른 값으로 업데이트되지 않도록 합니다.
- I열의 결과는 아래의 기준으로 도출됩니다. 만약 특별한 상황으로 결과가 변경되어야 할 경우 수동으로 업데이트합니다.
  * passed : "ok"가 0보다 크고, 나머지가 모두 0일 때
  * failed : "alarm"이 0보다 클 때
  * skipped
    * "info"가 0보다 크고, 나머지가 모두 0일 때
    * "error"가 0보다 클 때
    * 모든 항목이 0일 때
