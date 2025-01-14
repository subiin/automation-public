# automation-public

## 개요
### 목적
  * GCP 상에서 서비스 운영 시 자동화를 적용하여 효율성을 향상시킵니다.

### 파일 설명
  * cis-benchmark : CIS Benchmark 결과를 시트에 수동으로 작성하던 불편함을 줄입니다.
  * metric-screenshot : 모니터링 메트릭 스크린샷 생성 과정을 자동화하여 일관된 좌표의 이미지를 빠르게 생성합니다.
  * quota-monitoring : 프로젝트별 Quota의 사용현황을 모니터링하여 지정한 threshold 초과 시 alert를 발생시켜 관리자에게 알립니다.
  * sa-key-exp-cicd : CI/CD 파이프라인을 구축하여 GCP 프로젝트 내 Service Account key(USER_MANAGED)의 만료일 이전에 slack 알림을 발생시킵니다.
  * sa-key-exp-serverless : Cloud Functions을 이용하여 GCP 프로젝트 내 Service Account key(USER_MANAGED)의 만료일 이전에 slack 알림을 발생시킵니다.
