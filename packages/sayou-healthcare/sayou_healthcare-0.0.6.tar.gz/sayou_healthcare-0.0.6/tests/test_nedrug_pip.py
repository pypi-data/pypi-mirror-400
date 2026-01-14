#!/usr/bin/env python3
"""
Nedrug Crawler 사용 예시
"""

from sayou.healthcare.nedrug import NedrugCrawler

def demo_download_excel(crawler: NedrugCrawler):
    """NEDRUG 다운로드 데모"""
    print(f"\n{'='*60}")
    print(f"NEDRUG Excel Download")
    print('='*60)

    data = crawler.download()
    for medicine in data.medicines:
        print(medicine)

def demo_parsing_excel(crawler: NedrugCrawler):
    """NEDRUG 다운로드 데모"""
    print(f"\n{'='*60}")
    print(f"NEDRUG Excel Parsing")
    print('='*60)

    data = crawler.parse()
    for medicine in data.medicines:
        print(medicine)

def main():
    """메인 데모 실행"""
    
    # Nedrug Crawler 초기화
    crawler = NedrugCrawler()
   
    # 각 파일링 타입 데모
    #demo_download_excel(crawler)
    demo_parsing_excel(crawler)
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)


if __name__ == "__main__":
    main()
