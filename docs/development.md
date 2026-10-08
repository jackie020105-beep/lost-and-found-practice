# 개발 안내

## 구성과 요청 처리

기존 `architecture.md`의 Flask 앱 팩토리 + SQLite 구조를 구현했습니다.
해당 문서의 후속 항목 중 입력 폼 CSRF 보호, 분류·검색·페이지 나누기,
습득일과 보관 장소 입력은 현재 구현에 포함되어 있습니다.

- `app/__init__.py`: `create_app()`으로 앱과 확장 기능을 구성합니다.
- `app/routes.py`: HTTP 요청을 처리하고 DB 결과를 화면에 전달합니다.
- `app/forms.py`: 등록 필드와 서버 측 입력 검증을 관리합니다.
- `app/db.py`: 요청마다 연결을 재사용하고 요청 종료 시 닫습니다.
- `app/templates/`: Jinja 템플릿에서 사용자 입력을 자동 이스케이프합니다.

등록 요청은 CSRF 검사 → 입력 검증 → SQL 저장 → 상세 페이지 이동 순서로 처리합니다.
검색과 저장의 사용자 입력은 SQL 매개변수로 전달합니다.

## URL

| 메서드 | 경로 | 기능 |
| --- | --- | --- |
| GET | `/` | 목록, `q` 검색어, `category` 분류, `page` 페이지 |
| GET | `/items/new` | 습득물 등록 화면 |
| POST | `/items/new` | 입력 검증 후 저장 |
| GET | `/items/<id>` | 상세 정보 |

등록 성공은 302 리다이렉트, 입력 오류는 422, CSRF 오류는 400,
존재하지 않는 물품이나 페이지는 404를 반환합니다.

## 데이터와 설정

`items` 테이블에 물품 정보를 저장합니다. `found_date`는 `YYYY-MM-DD` 형식이며,
`created_at`은 SQLite의 UTC 생성 시각입니다. 습득일의 기본값과 미래 날짜 검사는
실행 환경의 로컬 날짜를 기준으로 합니다.

초기화는 `CREATE TABLE IF NOT EXISTS`를 사용하므로 기존 행을 삭제하지 않습니다.
테이블 구조가 바뀌면 DB 백업과 마이그레이션을 별도로 준비해야 합니다.

`SECRET_KEY` 환경변수로 세션 서명 키를 지정할 수 있습니다.
설정하지 않으면 로컬 개발을 위해 앱 생성 시 임의 키를 만듭니다.
이 경우 서버를 재시작하면 기존 브라우저의 CSRF 토큰이 무효가 되므로 등록 화면을 새로 열어주세요.
여러 프로세스로 배포할 때는 동일한 비밀 키를 환경변수로 제공해야 합니다.
이 프로젝트는 `.env` 파일을 자동으로 읽지 않습니다.

```powershell
# 키 생성 후 출력된 값을 SECRET_KEY 환경변수로 설정합니다.
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
$env:SECRET_KEY = "위에서 생성한 키"
```

## 후속 개발

1. 학교 계정 로그인 및 등록자·관리자 권한
2. 소유자 확인, 반환 상태 변경, 처리 이력
3. 사진 업로드와 파일 형식·용량 검증
4. 운영 WSGI 서버, HTTPS, 고정 비밀 키, DB 백업 설정

현재 등록 화면은 모든 방문자가 사용할 수 있습니다. 로그인과 권한 구현 후
학교에서 공개 운영하는 범위로 확장하세요.

## 참고 문서

- [Flask 공식 문서: SQLite 연결과 앱 등록](https://flask.palletsprojects.com/en/stable/tutorial/database/)
- [Flask-WTF 공식 문서: CSRF 보호](https://flask-wtf.readthedocs.io/en/1.2.x/csrf/)
