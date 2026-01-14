#!/usr/bin/env python3
"""
Hira Crawler 사용 예시
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

from sayou.healthcare.hira import HiraCrawler

def demo_download_medicines(crawler: HiraCrawler):
    """Hira 다운로드 데모"""
    print(f"\n{'='*60}")
    print(f"건강보험심사평가원")
    print('='*60)

    data = crawler.download()
    for medicine in data.medicines:
        print(medicine)

def demo_parsing_medicines(crawler: HiraCrawler):
    """NEDRUG 다운로드 데모"""
    print(f"\n{'='*60}")
    print(f"Parsing NEDRUG Excel")
    print('='*60)

    data = crawler.parse()
    for medicine in data.medicines:
        print(medicine)

def demo_download_opendata(crawler: HiraCrawler):
    """Hira 다운로드 데모"""
    print(f"\n{'='*60}")
    print(f"보건의료빅데이터개방시스템 데이터 다운로드")
    print('='*60)

    data = crawler.opendata()    
    print(f"Download File: {data.download_file.filename}")
    print(f"Extracted Files: {data.extracted_files}")
    print(f"Hospital Data: {data.hospital_data.filename}")
    for hospital in data.hospital_data.rows:
        print(hospital)
    print(f"Pharmacy Data: {data.pharmacy_data.filename}")
    for pharmacy in data.pharmacy_data.rows:
        print(pharmacy)

    print("\nOpenData Hospitals")
    hospitals = crawler.hospitals()
    for hospital in hospitals.rows:
        print(hospital)

    print("\nOpenData Pharmacies")
    pharmacies = crawler.pharmacies()
    for pharmacy in pharmacies.rows:
        print(pharmacy)

def main():
    """메인 데모 실행"""
    
    # Hira Crawler 초기화
    crawler = HiraCrawler()
   
    # 각 파일링 타입 데모
    #demo_download_medicines(crawler)
    demo_download_opendata(crawler)
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)


if __name__ == "__main__":
    main()
