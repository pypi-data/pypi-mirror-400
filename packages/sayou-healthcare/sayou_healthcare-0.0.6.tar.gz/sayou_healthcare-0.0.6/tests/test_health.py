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

from sayou.healthcare.health import HealthCrawler

def demo_download(crawler: HealthCrawler):
    """약학정보원 > 의약품검색 데모"""
    print(f"\n{'='*60}")
    print(f"약학정보원 > 의약품검색 > 검색")
    print('='*60)

    medicines = crawler.medicines()    
    for medicine in medicines:
        #print(medicine)
        pass

def main():
    """약학정보원 데모 실행"""
    
    # Health Crawler 초기화
    crawler = HealthCrawler()
   
    # 각 파일링 타입 데모
    demo_download(crawler)
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)


if __name__ == "__main__":
    main()
