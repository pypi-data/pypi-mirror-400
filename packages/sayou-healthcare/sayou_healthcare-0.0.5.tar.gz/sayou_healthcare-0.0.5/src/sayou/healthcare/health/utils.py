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

import re
from urllib.parse import unquote

_HEALTH_START_URL_ = "https://www.health.kr/searchDrug/search_detail.asp"
_HEALTH_BASE_URL_ = "https://www.health.kr/searchDrug/result_more.asp"

KOREAN_INITIAL = "%E3%84%B1"
KOREAN_INITIALS = ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ", 
                   "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

def decode_euc_kr(response):
    """깨진 한글 인코딩 복원"""
    
    # 인코딩 변환 (EUC-KR Bytes -> Python Unicode String)
    # response.text를 바로 쓰지 않고, content(바이트)를 직접 디코딩하는 것이 안전합니다.
    try:
        content = response.content.decode('euc-kr')
        return content
    except UnicodeDecodeError:
        # euc-kr로 안 될 경우 cp949 시도 (확장 완성형)
        content = response.content.decode('cp949', errors='replace')
    
    return content

def get_filename(headers):
    content_disposition = headers.get("Content-Disposition", "")
    # filename="..." 또는 filename*=UTF-8''... 패턴 찾기
    matches = re.findall("filename=\"(.+)\"", content_disposition)
    if len(matches) == 0:
        return None
    
    encoded_filename = matches[0]
    filename = encoded_filename.encode('latin1').decode('utf-8')
    print('Content-Disposition', content_disposition)
    print('filename', filename)

    return filename

def _get_filename(headers):
    filename = None

    content_disposition = headers.get("Content-Disposition", "")
    # filename="..." 또는 filename*=UTF-8''... 패턴 찾기
    match = re.search(r"filename\*?=['\"]?(?:UTF-8'')?([^'\";\n]+)", content_disposition)
    if match:
        filename = match.group(1)

        # URL 인코딩된 경우
        if '%' in filename:
            filename = unquote(filename)
        
        # 깨진 인코딩 복원
        filename = decode_euc_kr(filename)
            
        # .zip 확장자 제거하여 폴더명으로 사용
        #save_path = filename.replace('.zip', '')

    return filename