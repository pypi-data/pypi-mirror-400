#!/usr/bin/env python3
"""
Nedrug Crawler 사용 예시
"""

import os
import pandas as pd
import sys

from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# 상위 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print(str(Path(__file__).parent.parent / 'src'))

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
