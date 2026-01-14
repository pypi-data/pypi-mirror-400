import re
from urllib.parse import unquote

_START_URL_ = "https://www.hira.or.kr/bbsDummy.do?pgmid=HIRAA030014050000"
_DOWNLOAD_BASE_URL_ = "https://www.hira.or.kr/bbs/bbsCDownLoad.do"

_HEALTH_START_URL_ = "https://www.health.kr/searchDrug/result_more.asp"
_HEALTH_BASE_URL_ = "https://www.hira.or.kr/bbs/bbsCDownLoad.do"
_HEALTH_DOWNLOAD_URL_ = "https://www.hira.or.kr/bbs/bbsCDownLoad.do"

KOREAN_INITIAL = "%E3%84%B1"
"""
KOREAN_INITIALS = {
    "ㄱ" : "%E3%84%B1",
    "ㄴ" : "%E3%84%B4",
    "ㄷ" : "%E3%84%B7",
    "ㄹ" : "%E3%84%B9",
    "ㅁ" : "%E3%85%81",
    "ㅂ" : "%E3%85%82",
    "ㅅ" : "%E3%85%85",
    "ㅇ" : "%E3%85%87",
    "ㅈ" : "%E3%85%88",
    "ㅊ" : "%E3%85%8A",
    "ㅋ" : "%E3%85%8B",
    "ㅌ" : "%E3%85%8C",
    "ㅍ" : "%E3%85%8D",
    "ㅎ" : "%E3%85%8E",
}
"""
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