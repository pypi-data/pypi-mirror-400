# sayou-healthcare

- 의약품안전나라 > 의약품등 제품정보 검색
- 건강보험심사평가원 > 약제급여목록표 > 약제정보
- 보건의료빅데이터개방시스템 > 공공데이터 > 전국 병의원 및 약국 현황
- 약학정보원 > 의약품 상세검색

#### 사이트 링크
- [건강보험심사평가원](https://www.hira.or.kr/main.do)
- [보건의료빅데이터개방시스템](https://opendata.hira.or.kr/home.do)
- [약학정보원](https://www.health.kr)
- [의약품 안전나라](https://nedrug.mfds.go.kr/index)

## 설치

```bash
pip install sayou-healthcare
```

## 사용 예시

#### 약학정보원 > 의약품 상세검색

```python
from sayou.healthcare.health import HealthCrawler

# Health Crawler 초기화
crawler = HealthCrawler()

medicines = crawler.medicines()    
for medicine in medicines:
    print(medicine)
```

#### 건강보험심사평가원 > 약제급여목록표 > 약제정보

```python
from sayou.healthcare.hira import HiraCrawler

# Hira Crawler 초기화
crawler = HiraCrawler()

data = crawler.download()
for medicine in data.medicines:
    print(medicine)
```

#### 보건의료빅데이터개방시스템 > 공공데이터 > 전국 병의원 및 약국 현황

```python
from sayou.healthcare.hira import HiraCrawler

# Hira Crawler 초기화
crawler = HiraCrawler()

data = crawler.opendata()    
print(f"Download File: {data.download_file.filename}")
print(f"Extracted Files: {data.extracted_files}")

print(f"Hospital Data: {data.hospital_data.filename}")
for hospital in data.hospital_data.rows:
    print(hospital)

print(f"Pharmacy Data: {data.pharmacy_data.filename}")
for pharmacy in data.pharmacy_data.rows:
    print(pharmacy)
```

#### 의약품안전나라 > 의약품등 제품정보 검색

```python
from sayou.healthcare.nedrug import NedrugCrawler

# Nedrug Crawler 초기화
crawler = NedrugCrawler()

data = crawler.download()
for medicine in data.medicines:
    print(medicine)
```
