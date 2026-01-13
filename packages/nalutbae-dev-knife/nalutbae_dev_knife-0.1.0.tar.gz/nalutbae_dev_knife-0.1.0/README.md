# Nalutbae DevKnife Toolkit

Python으로 구현된 일상적인 개발자 유틸리티를 통합한 올인원 터미널 툴킷입니다.

## 기능

- **인코딩/디코딩**: Base64, URL 인코딩 등
- **데이터 형식 처리**: JSON, XML, YAML 포맷팅 및 변환
- **데이터 변환**: CSV/TSV를 Markdown으로 변환
- **개발자 도구**: UUID 생성, IBAN 검증, 패스워드 생성
- **수학적 변환**: 진법 변환, 해시 생성, 타임스탬프 변환
- **웹 개발 도구**: GraphQL 포맷팅, CSS 처리, URL 추출

## 인터페이스

- **CLI**: 명령줄에서 직접 실행
- **TUI**: 대화형 터미널 인터페이스

## 설치

### PyPI에서 설치 (권장)

```bash
# 최신 안정 버전 설치
pip install nalutbae-dev-knife

# 설치 확인
devknife --version
devknife --help
```

### 소스에서 설치 (개발용)

```bash
# 저장소 클론
git clone https://github.com/nalutebae/nalutbae-dev-knife.git
cd nalutbae-dev-knife

# 개발 모드로 설치
pip install -e ".[dev]"

# 또는 설치 스크립트 사용
python scripts/install.py --dev
```

### 요구사항

- Python 3.8 이상
- pip (Python 패키지 설치 도구)

## 사용법

### 설치 후 개발 모드로 실행
```bash
# 현재 개발 중인 버전을 설치
pip install -e .

# 사용 가능한 명령어 확인
devknife --help
devknife list-commands
```

### 인코딩/디코딩 유틸리티

#### Base64 인코딩/디코딩
```bash
# Base64 인코딩
devknife base64 'Hello World!'
# 출력: SGVsbG8gV29ybGQh

# Base64 디코딩
devknife base64 --decode 'SGVsbG8gV29ybGQh'
# 출력: Hello World!

# 파이프를 통한 입력
echo 'Hello World!' | devknife base64

# 파일에서 읽기
devknife base64 --file input.txt

# 도움말
devknife base64 --help
```

#### URL 인코딩/디코딩
```bash
# URL 인코딩
devknife url 'Hello World! @#$%'
# 출력: Hello%20World%21%20%40%23%24%25

# URL 디코딩
devknife url --decode 'Hello%20World%21%20%40%23%24%25'
# 출력: Hello World! @#$%

# 파이프를 통한 입력
echo 'Hello World! @#$%' | devknife url

# 파일에서 읽기
devknife url --file input.txt

# 도움말
devknife url --help
```

### 데이터 형식 처리 유틸리티

#### JSON 포맷팅
```bash
# JSON 포맷팅 (압축된 JSON을 읽기 쉽게)
devknife json '{"name":"John","age":30,"city":"Seoul"}'
# 출력:
# {
#   "name": "John",
#   "age": 30,
#   "city": "Seoul"
# }

# 사용자 정의 들여쓰기
devknife json --indent 4 '{"name":"John","age":30}'

# JSON 복구 모드 (손상된 JSON 자동 수정)
devknife json --recover "{'name':'John','age':30,}"
# 출력: 유효한 JSON으로 변환됨

# 파이프를 통한 입력
echo '{"compressed":"json"}' | devknife json

# 파일에서 읽기
devknife json --file data.json

# 도움말
devknife json --help
```

#### JSON을 YAML로 변환
```bash
# JSON을 YAML로 변환
devknife json2yaml '{"name":"John","age":30,"hobbies":["reading","coding"]}'
# 출력:
# name: John
# age: 30
# hobbies:
# - reading
# - coding

# 중첩된 객체 변환
devknife json2yaml '{"person":{"name":"John","details":{"age":30,"city":"Seoul"}}}'

# 파이프를 통한 입력
echo '{"database":{"host":"localhost","port":5432}}' | devknife json2yaml

# 파일에서 읽기
devknife json2yaml --file config.json

# 도움말
devknife json2yaml --help
```

#### XML 포맷팅
```bash
# XML 포맷팅 (압축된 XML을 읽기 쉽게)
devknife xml '<root><person><name>John</name><age>30</age></person></root>'
# 출력:
# <?xml version="1.0" ?>
# <root>
#   <person>
#     <name>John</name>
#     <age>30</age>
#   </person>
# </root>

# 사용자 정의 들여쓰기
devknife xml --indent 4 '<root><item>value</item></root>'

# 파이프를 통한 입력
echo '<config><database><host>localhost</host></database></config>' | devknife xml

# 파일에서 읽기
devknife xml --file config.xml

# 도움말
devknife xml --help
```

#### JSON을 Python 클래스로 변환
```bash
# JSON 구조를 Python 데이터클래스로 변환
devknife json2py '{"name":"John","age":30,"active":true}' --class-name Person
# 출력:
# from dataclasses import dataclass
# from typing import Any, List, Dict, Optional
# 
# @dataclass
# class Person:
#     name: str
#     age: int
#     active: bool

# 복잡한 중첩 구조
devknife json2py '{"id":1,"user":{"name":"John","hobbies":["reading","coding"]}}' --class-name UserData

# 기본 클래스명 사용
devknife json2py '{"test":"value"}'  # GeneratedClass로 생성됨

# 파이프를 통한 입력
echo '{"id":1,"title":"Task","completed":false}' | devknife json2py --class-name Task

# 파일에서 읽기
devknife json2py --file schema.json --class-name MyClass

# 도움말
devknife json2py --help
```

### 💡 사용 팁

#### 따옴표 사용법
```bash
# ✅ 권장: 단일 따옴표 사용
devknife base64 'Hello World!'
echo 'Hello World!' | devknife base64

# ❌ 피하기: 이중 따옴표는 쉘에서 문제를 일으킬 수 있음
devknife base64 "Hello World!"  # 문제 발생 가능
```

#### 다양한 입력 방법
```bash
# 1. 직접 인수로 전달
devknife base64 '텍스트'

# 2. 파이프를 통한 전달
echo '텍스트' | devknife base64

# 3. 파일에서 읽기
devknife base64 --file filename.txt

# 4. 표준 입력에서 읽기 (대화형)
devknife base64  # 엔터 후 텍스트 입력
```

### TUI 모드 (개발 예정)
```bash
# 대화형 터미널 인터페이스 시작
devknife
```

### 현재 구현된 기능
- ✅ Base64 인코딩/디코딩
- ✅ URL 인코딩/디코딩
- ✅ JSON/XML/YAML 처리
- 🚧 CSV/TSV 변환 (개발 중)
- 🚧 개발자 도구 (개발 중)
- 🚧 수학적 변환 (개발 중)
- 🚧 웹 개발 도구 (개발 중)

## 실제 사용 예시

### Base64 인코딩/디코딩 예시
```bash
# 간단한 텍스트 인코딩
$ devknife base64 'Hello DevKnife!'
SGVsbG8gRGV2S25pZmUh

# 디코딩해서 원본 확인
$ devknife base64 --decode 'SGVsbG8gRGV2S25pZmUh'
Hello DevKnife!

# 특수문자가 포함된 텍스트
$ devknife base64 '안녕하세요! 🚀'
7JWI64WV7ZWY7IS47JqUISAg8J+agA==

# 파일 내용 인코딩
$ echo 'This is a secret message' > secret.txt
$ devknife base64 --file secret.txt
VGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl
```

### URL 인코딩/디코딩 예시
```bash
# 공백과 특수문자가 있는 URL 인코딩
$ devknife url 'Hello World! How are you?'
Hello%20World%21%20How%20are%20you%3F

# 한글 URL 인코딩
$ devknife url '안녕하세요 개발자님!'
%EC%95%88%EB%85%95%ED%95%98%EC%84%B8%EC%9A%94%20%EA%B0%9C%EB%B0%9C%EC%9E%90%EB%8B%98%21

# URL 디코딩
$ devknife url --decode 'Hello%20World%21%20How%20are%20you%3F'
Hello World! How are you?

# 복잡한 쿼리 스트링 처리
$ devknife url 'name=John Doe&email=john@example.com&message=Hello there!'
name%3DJohn%20Doe%26email%3Djohn%40example.com%26message%3DHello%20there%21
```

### JSON/XML/YAML 처리 예시
```bash
# 압축된 JSON을 읽기 쉽게 포맷팅
$ devknife json '{"name":"김철수","age":25,"skills":["Python","JavaScript","Go"]}'
{
  "name": "김철수",
  "age": 25,
  "skills": [
    "Python",
    "JavaScript",
    "Go"
  ]
}

# 손상된 JSON 복구
$ devknife json --recover "{'name':'김철수','age':25,}"
{
  "name": "김철수",
  "age": 25
}

# JSON을 YAML로 변환
$ devknife json2yaml '{"database":{"host":"localhost","port":5432,"credentials":{"username":"admin","password":"secret"}}}'
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret

# XML 포맷팅
$ devknife xml '<config><server><host>localhost</host><port>8080</port></server></config>'
<?xml version="1.0" ?>
<config>
  <server>
    <host>localhost</host>
    <port>8080</port>
  </server>
</config>

# JSON을 Python 클래스로 변환
$ devknife json2py '{"user_id":123,"profile":{"name":"김철수","email":"kim@example.com","preferences":{"theme":"dark","language":"ko"}}}' --class-name UserProfile
from dataclasses import dataclass
from typing import Any, List, Dict, Optional

@dataclass
class UserProfile:
    user_id: int
    profile: Dict[str, Any]
```

### 실무 활용 예시
```bash
# API 응답 JSON 포맷팅
$ curl -s https://api.example.com/users/1 | devknife json

# 설정 파일 JSON을 YAML로 변환
$ devknife json2yaml --file config.json > config.yaml

# 로그 파일에서 JSON 추출 후 포맷팅
$ grep '{"timestamp"' app.log | devknife json

# API 스키마를 Python 클래스로 변환
$ devknife json2py --file api_schema.json --class-name ApiResponse > models.py

# XML 설정 파일 정리
$ devknife xml --file web.config --indent 4 > web_formatted.config
```

### 파이프라인 활용 예시
```bash
# 여러 명령어 조합
$ echo 'Hello World!' | devknife base64 | devknife base64 --decode
Hello World!

# 파일 처리 파이프라인
$ cat data.txt | devknife url | tee encoded.txt
$ cat encoded.txt | devknife url --decode
```

## 문제 해결

### 자주 발생하는 문제

#### `dquote>` 프롬프트가 나타날 때
```bash
# 문제: 이중 따옴표 사용으로 인한 쉘 파싱 오류
$ devknife base64 "Hello World!"
dquote>

# 해결: Ctrl+C로 취소 후 단일 따옴표 사용
$ devknife base64 'Hello World!'
SGVsbG8gV29ybGQh
```

#### 한글이나 특수문자 처리
```bash
# UTF-8 인코딩이 제대로 처리됨
$ devknife base64 '한글 테스트 🎉'
7ZWc6riAIO2FjOyKpO2KuCDwn46J

$ devknife base64 --decode '7ZWc6riAIO2FjOyKpO2KuCDwn46J'
한글 테스트 🎉
```

#### 긴 텍스트나 파일 처리
```bash
# 큰 파일은 --file 옵션 사용 권장
$ devknife base64 --file large_file.txt

# 또는 파이프 사용
$ cat large_file.txt | devknife base64
```

#### JSON 관련 문제
```bash
# 잘못된 JSON 형식
$ devknife json '{"name":"John","age":30,}'
오류: Invalid JSON format: Expecting property name enclosed in double quotes: line 1 column 25 (char 24). Use --recover flag to attempt automatic repair.

# 복구 모드 사용
$ devknife json --recover '{"name":"John","age":30,}'
{
  "name": "John",
  "age": 30
}

# 단일 따옴표 JSON 복구
$ devknife json --recover "{'name':'John','age':30}"
{
  "name": "John",
  "age": 30
}
```

#### XML 관련 문제
```bash
# 잘못된 XML 형식
$ devknife xml '<root><unclosed>'
오류: Invalid XML format: mismatched tag: line 1, column 15

# 올바른 XML 사용
$ devknife xml '<root><item>value</item></root>'
<?xml version="1.0" ?>
<root>
  <item>value</item>
</root>
```

### 오류 메시지 해석

#### Base64 디코딩 오류
```bash
$ devknife base64 --decode 'invalid base64!'
오류: Invalid Base64 format. Base64 strings should only contain A-Z, a-z, 0-9, +, /, and = for padding.
```

#### JSON 처리 오류
```bash
# 잘못된 JSON 형식
$ devknife json '{"name":"John",}'
오류: Invalid JSON format: Expecting property name enclosed in double quotes: line 1 column 15 (char 14). Use --recover flag to attempt automatic repair.

# JSON to YAML 변환 오류
$ devknife json2yaml '{"name":"John",}'
오류: Invalid JSON input: Expecting property name enclosed in double quotes: line 1 column 15 (char 14)

# JSON to Python 클래스 변환 오류
$ devknife json2py '{"name":"John",}'
오류: Invalid JSON input: Expecting property name enclosed in double quotes: line 1 column 15 (char 14)
```

#### XML 처리 오류
```bash
$ devknife xml '<root><unclosed>'
오류: Invalid XML format: mismatched tag: line 1, column 15
```

#### 입력 없음 오류
```bash
$ devknife base64
오류: 입력 텍스트가 필요합니다. --help를 참조하세요.

$ devknife json
오류: 입력 텍스트가 필요합니다. --help를 참조하세요.
```

## 개발

### 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/nalutebae/nalutbae-dev-knife.git
cd nalutbae-dev-knife

# 가상 환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 개발 의존성과 함께 설치
pip install -e ".[dev]"
```

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 테스트
pytest --cov=devknife

# 속성 기반 테스트만 실행
pytest -k "property"
```

### 코드 품질 검사

```bash
# 코드 포맷팅
black devknife tests

# 린팅
flake8 devknife tests

# 타입 체크
mypy devknife
```

### 패키지 빌드

```bash
# 빌드 스크립트 사용 (권장)
python scripts/build.py

# 수동 빌드
python -m build
```

### 배포

```bash
# Test PyPI에 업로드 (테스트용)
python -m twine upload --repository testpypi dist/*

# PyPI에 업로드 (프로덕션)
python -m twine upload dist/*

# 자동화된 릴리스 (버전 범프 포함)
python scripts/release.py patch  # 패치 버전 증가
python scripts/release.py minor  # 마이너 버전 증가
python scripts/release.py major  # 메이저 버전 증가
```

### 기여하기

기여에 관심이 있으시면 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

### 상세한 설정 가이드

개발 환경 설정에 대한 자세한 내용은 [SETUP.md](SETUP.md)를 참조하세요.

## 라이선스

MIT License