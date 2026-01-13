# NFCL (New Fantastic Comsigan Loader)

[![PyPI version](https://badge.fury.io/py/NFCL.svg)](https://badge.fury.io/py/NFCL)

컴시간알리미 웹사이트에서 학교 시간표 데이터를 가져오는 Python 라이브러리입니다. Selenium을 사용하여 동적 페이지를 크롤링하며, 학교 이름, 학년, 반 정보를 입력하여 주간 시간표를 JSON 형식으로 받아올 수 있습니다.

## 주요 기능

- **시간표 추출**: 월요일부터 금요일까지의 교시별 과목 및 담당 교사 정보를 추출합니다.

## 설치 방법

```bash
pip install NFCL
```

*참고: Chrome 브라우저가 설치되어 있어야 합니다.*

## 사용 방법

### 1. 간단한 함수 호출 방식
```python
import nfcl

# 학교명, 학년, 반 입력
result = nfcl.get_timetable("인천과학고등학교", 1, 1)
print(result)
```

### 2. 클래스 인스턴스 사용 방식 (상세 설정 가능)
```python
from nfcl import ComciganAPI

# API 객체 생성 (headless=False로 설정하면 브라우저 창이 보입니다)
api = ComciganAPI(headless=True)

# 시간표 가져오기
result = api.get_timetable("인천과학고등학교", 1, 1)

if "error" in result:
    print(f"에러 발생: {result['error']}")
else:
    print(f"학교: {result['school']}")
    print(f"학급: {result['class']}")
```

### 결과 데이터 구조

```json
{
    "school": "학교명",
    "class": "1-1",
    "timetable": {
        "월": [
            {"period": "1", "subject": "수학", "teacher": "홍길"},
            ...
        ],
        "화": [...],
        "수": [...],
        "목": [...],
        "금": [...]
    }
}
```

## 의존성

- [selenium](https://pypi.org/project/selenium/)
- [webdriver-manager](https://pypi.org/project/webdriver-manager/)

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
