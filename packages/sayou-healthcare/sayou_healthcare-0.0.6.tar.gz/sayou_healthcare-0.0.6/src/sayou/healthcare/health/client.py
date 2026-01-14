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
 
import requests
import time

class HealthClient:
    """
    클라이언트
    건강보험심사평가원 > 약제급여목록표 > 약제정보 
    """

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                  "image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/131.0.0.0 Safari/537.36"
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._rate_limit_delay = 0.1  # OpenDart 요청 제한 준수

    def _rate_limit(self):
        """API 호출 제한"""
        time.sleep(self._rate_limit_delay)

    def _get(self, url: str, params: dict = None, headers: dict = None, referer: str = None, timeout: int = 10) -> requests.Response:
        """GET 요청 (rate limit 적용)"""
        self._rate_limit()
        
        if referer:
            self.session.headers.update({'Referer': referer})
        
        response = self.session.get(url, params=params, headers=headers, timeout=timeout)

        response.raise_for_status()
        response.encoding = 'utf-8'

        return response

    def _post(self, url: str, params: dict = None, body: dict = None, headers: dict = None, referer: str = None, timeout: int = 10) -> requests.Response:
        """POST 요청 (rate limit 적용)"""
        self._rate_limit()
        
        if referer:
            self.session.headers.update({'Referer': referer})
        
        if params:
            response = self.session.post(url, params=params, data=body, headers=headers, timeout=timeout)
        else:
            response = self.session.post(url, data=body, headers=headers, timeout=timeout)

        response.raise_for_status()
        response.encoding = 'utf-8'

        return response