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

```python
from sayou.healthcare.health import HealthCrawler

# SEC에서 요구하는 User-Agent 설정
crawler = HealthCrawler()

# 각 파일링 타입 데모
demo_download(crawler)

print("\n" + "="*60)
print("Demo completed!")
print("="*60)


if __name__ == "__main__":
    main()
```
