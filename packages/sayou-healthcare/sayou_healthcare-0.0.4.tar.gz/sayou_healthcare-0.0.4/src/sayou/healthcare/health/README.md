# Health Crawler

```text
약학정보원 > 의약품 상세검색 > 초성별 검색
급여 + 비급여 약품 포함
업로드 주기: xxx

의약품 상세검색 (기본 페이지):
https://www.health.kr/searchDrug/search_detail.asp
검색결과 리스트 (검색 결과):
https://www.health.kr/searchDrug/search_detail.asp
검색결과 더보기:
https://www.health.kr/searchDrug/result_more.asp
의약품 상세정보
https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2018061800005

1. 초성 "ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅅ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ"
2. 페이지 사이즈 : 1000
3. xpath으로 약품목록 파싱
4. BigQuery에 로드
5. medicine_list.csv에 저장
```