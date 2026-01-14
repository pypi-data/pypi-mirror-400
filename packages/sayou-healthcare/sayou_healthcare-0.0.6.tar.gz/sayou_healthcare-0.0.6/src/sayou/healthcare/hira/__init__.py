# Copyright (c) 2025-2026, Sayouzone
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
 
"""
Hira Crawler
===========================

Hira에서 주요 데이터를 추출하는 Python 패키지

Installation:
    pip install requests beautifulsoup4 lxml openpyxl

Quick Start:
    >>> from sayou.healthcare.hira import HiraCrawler
    >>> 
    >>> crawler = HiraCrawler()
    >>> 
    >>> # 건강보험심사평가원 약품목록 다운로드
    >>> data = crawler.download()
    >>> for medicine in data.medicines:
    >>>     print(medicine)
    >>>
    >>> # 다운로드된 엑셀 파일 파싱
    >>> data = crawler.parse()
    >>> for medicine in data.medicines:
    >>>     print(medicine)
    >>> 
    >>> # 보건의료빅데이터개방시스템
    >>> data = crawler.opendata()    
    >>> print(f"Download File: {data.download_file.filename}")
    >>> print(f"Extracted Files: {data.extracted_files}")
    >>> print(f"Hospital Data: {data.hospital_data.filename}")
    >>> for hospital in data.hospital_data.rows:
    >>>     print(hospital)
    >>> print(f"Pharmacy Data: {data.pharmacy_data.filename}")
    >>> for pharmacy in data.pharmacy_data.rows:
    >>>     print(pharmacy)
    >>>
    >>> # OpenData Hospitals
    >>> hospitals = crawler.hospitals()
    >>> for hospital in hospitals.rows:
    >>>     print(hospital)
    >>>
    >>> # OpenData Pharmacies
    >>> pharmacies = crawler.pharmacies()
    >>> for pharmacy in pharmacies.rows:
    >>>     print(pharmacy)

Supported Cases:
    - 건강보험심사평가원 약품목록 다운로드
    - 다운로드된 엑셀 파일 파싱
    - 보건의료빅데이터개방시스템 병원 및 약국

Note:
    Hira에서 User-Agent를 사용하세요.
"""

__version__ = "0.1.0"
__author__ = "SeongJung Kim"

from .crawler import HiraCrawler
from .client import HiraClient
from .models import (
    BoardItem,
    DownloadFile,
    DownloadResult,
    ExcelData,
    FileType,
    Hospital,
    OpenDataResult,
    Pharmacy,
)
from .parsers import (
    ExcelParser,
    DownloadParser,
    OpenDataParser,
)

__all__ = [
    # 메인 클래스
    "HiraCrawler",
    "HiraClient",
    
    # 데이터 모델
    "BoardItem",
    "DownloadFile",
    "DownloadResult",
    "ExcelData",
    "FileType",
    "Hospital",
    "OpenDataResult",
    "Pharmacy",
    
    # 파서
    "ExcelParser",
    "DownloadParser",
    "OpenDataParser",
]
