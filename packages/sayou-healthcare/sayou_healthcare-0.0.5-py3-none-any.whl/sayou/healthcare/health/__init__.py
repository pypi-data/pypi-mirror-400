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
Health Crawler
===========================

Health에서 주요 데이터를 추출하는 Python 패키지

Installation:
    pip install requests beautifulsoup4 lxml

Quick Start:
    >>> from sayou.healthcare.health import HealthCrawler
    >>> 
    >>> crawler = HealthCrawler()
    >>> 
    >>> # 의약품목록 다운로드
    >>> medicines = crawler.medicines()
    >>> for medicine in medicines:
    >>>     print(medicine)

Supported Cases:
    - 의약품목록 다운로드

Note:
    Health에서 User-Agent를 사용하세요.
"""

__version__ = "0.1.0"
__author__ = "SeongJung Kim"

from .crawler import HealthCrawler
from .client import HealthClient
from .models import (
    Medicine,
    SearchPayload,
)
from .parsers import (
    DownloadParser,
)

__all__ = [
    # 메인 클래스
    "HealthCrawler",
    "HealthClient",
    
    # 데이터 모델
    "Medicine",

    # 파서
    "DownloadParser",
]
