# HIRA Crawler

약재정보 및 전국 병의원, 약국 현황

```text
건강보험심사평가원 > 약제급여목록표 > 약제정보 > 약제정보 다운로드
업로드 주기: 1개월

1. Excel 파일 다운로드
2. GCS에 업로드
3. Excel 파일에서 약품목록 파싱
4. BigQuery에 로드
5. medicine_list.csv에 저장
```

```text
보건의료빅데이터개방시스템 > 공공데이터 > 전국 병의원 및 약국 현황 다운로드
업로드 주기: 분기별

전국 병의원 및 약국 현황:
https://opendata.hira.or.kr/op/opc/selectOpenData.do?sno=11925
ZIP 파일 다운로드:
https://opendata.hira.or.kr/dext5upload/handler/upload.dx

1. 최신 ZIP 파일 식별
2. ZIP 파일 다운로드
3. ZIP 파일 압축 해제
4. GCS에 업로드
5. Excel 파일에서 약품목록 파싱
6. BigQuery에 로드
7. hospital_list.csv 및 pharmacy_list.csv 생성
```