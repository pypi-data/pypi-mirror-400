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
Nedrug Crawler
===========================

Nedrug에서 주요 데이터를 추출하는 Python 패키지

Installation:
    pip install requests beautifulsoup4 lxml openpyxl

Quick Start:
    >>> from sayou.healthcare.nedrug import NedrugCrawler
    >>> 
    >>> crawler = NedrugCrawler()
    >>> 
    >>> # Nedrug에서 약품목록 다운로드
    >>> data = crawler.download()
    >>> for medicine in data.medicines:
    >>>     print(medicine)
    >>> 
    >>> # Nedrug에서 약품목록 파싱
    >>> data = crawler.parse()
    >>> for medicine in data.medicines:
    >>>     print(medicine)

Supported Cases:
    - 약품목록 다운로드
    - 약품목록 파싱

Note:
    Nedrug에서 User-Agent를 사용하세요.
"""

__version__ = "0.1.0"
__author__ = "SeongJung Kim"

from .crawler import NedrugCrawler
from .client import NedrugClient
from .models import (
    CancelCode,
    DownloadFile,
    DownloadResult,
    EtcOtcCode,
    ExcelData,
    FileType,
    Medicine,
    PageResult,
    SearchParams,
)
from .parsers import (
    ExcelParser,
    DownloadParser,
)

__all__ = [
    # 메인 클래스
    "NedrugCrawler",
    "NedrugClient",
    
    # Enums
    "CancelCode",
    "EtcOtcCode",
    "FileType",
    # 데이터 모델
    "DownloadFile",
    "DownloadResult",
    "ExcelData",
    "Medicine",
    "PageResult",
    "SearchParams",

    # 파서
    "ExcelParser",
    "DownloadParser",
]
