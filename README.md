# 교내 분실물 관리 서비스

Python + Flask + SQLite로 만든 로컬 개발용 웹 서비스입니다.
학교에서 습득한 물건을 등록하고 목록·검색·상세 화면에서 확인할 수 있습니다.

## 시작하기

Python 3.10 이상이 필요합니다. 프로젝트 폴더의 PowerShell에서 실행하세요.
가상환경을 활성화하지 않고 해당 환경의 Python을 직접 사용합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

브라우저에서 <http://127.0.0.1:5000>에 접속하세요. 종료는 `Ctrl+C`입니다.
첫 실행 시 `instance/lost_and_found.sqlite3` 파일과 테이블이 자동 생성됩니다.

`python` 명령을 사용할 수 없고 `uv`가 설치되어 있다면 다음 명령을 사용하세요.

```powershell
uv venv .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

macOS / Linux에서는 `python3 -m venv .venv`로 생성하고,
위 명령의 `.\.venv\Scripts\python.exe`를 `.venv/bin/python`으로 바꾸면 됩니다.

## 폴더와 파일

```text
lost-and-found-practice/
├── app/
│   ├── __init__.py          # 앱 생성, 설정, 오류 처리
│   ├── db.py               # SQLite 연결 및 초기화 명령
│   ├── forms.py            # 등록 폼, 입력 검증, 분류 목록
│   ├── routes.py           # 목록, 검색, 등록, 상세 조회
│   ├── schema.sql          # DB 테이블과 인덱스
│   ├── templates/
│   │   ├── base.html       # 공통 레이아웃
│   │   ├── error.html      # 오류 화면
│   │   └── items/          # 목록, 등록, 상세 화면
│   └── static/css/         # 반응형 화면 스타일
├── docs/                   # 기존 설계 문서와 개발 안내
├── instance/               # 로컬 DB 저장 위치, 데이터는 Git 제외
├── tests/                  # 임시 DB를 사용하는 기능 테스트
├── .gitignore
├── requirements.txt        # 실행 의존성
├── run.py                  # 개발 서버 실행
└── README.md
```

## 구현된 기능

- 물품명, 분류, 습득 장소·날짜, 보관 장소, 설명 등록
- 최근 등록순 목록, 검색, 분류 필터, 12개 단위 페이지 나누기
- 분실물 상세 정보와 보관 장소 조회
- 필수 항목, 글자 수, 날짜 검증 및 등록 폼 CSRF 보호
- 한국어 화면, 모바일 대응, 빈 목록과 오류 안내

## 개발 및 테스트

```powershell
# 자동 새로고침을 사용하는 로컬 개발 서버
.\.venv\Scripts\python.exe -m flask --app app run --debug

# 기존 데이터를 보존하며 테이블 생성
.\.venv\Scripts\python.exe -m flask --app app init-db

# Python 표준 unittest로 기능 테스트
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

테스트는 별도의 임시 DB를 사용하며 실제 등록 데이터에 영향을 주지 않습니다.
`init-db`는 스키마 변경을 적용하는 마이그레이션 명령이 아닙니다.

현재 범위는 로그인 없는 습득물 게시 기능입니다. 학교 계정 로그인, 관리자 권한,
반환 처리, 사진 업로드는 후속 개발 항목입니다.
개발 서버는 로컬 주소로 실행됩니다. 공개 서비스로 전환할 때 필요한 작업과 설정은
[개발 안내](docs/development.md)에 정리했습니다.
