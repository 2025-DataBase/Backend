## 프로젝트 개요

이 프로젝트는 `Flask`와 `MySQL`을 사용하는 **헌터/악마/미션 관리 웹 애플리케이션**입니다.  
웹 브라우저에서 헌터, 악마, 전투, 미션 정보를 조회·등록·수정할 수 있습니다.

---

## 기술 스택 및 설치 라이브러리

- **언어**: Python 3.x (권장: 3.10 이상)
- **웹 프레임워크**: Flask
- **DB**: MySQL (`chain_db` 데이터베이스 사용)
- **Python 라이브러리 (pip로 설치 필요)**  
  - **flask**: 웹 서버 및 라우팅, 템플릿 렌더링 등에 사용  
  - **pymysql**: Python에서 MySQL 데이터베이스에 접속하기 위해 사용  

이외에 사용되는 모듈들은 Python 기본 라이브러리라, 따로 설치하지 않아도 됩니다.

필요한 외부 패키지는 `requirements.txt`에 정리되어 있습니다:

```bash
pip install -r requirements.txt
```

---

## 폴더 구조

```text
database_pJ/
├─ Backend/
│  ├─ chainTeamProject/
│  │  ├─ app/
│  │  │  ├─ __init__.py
│  │  │  ├─ routes.py
│  │  │  └─ templates/
│  │  │     ├─ base.html
│  │  │     ├─ battle_list.html
│  │  │     ├─ demon_list.html
│  │  │     ├─ hunter_detail.html
│  │  │     ├─ hunter_form.html
│  │  │     ├─ hunter_list.html
│  │  │     ├─ mission_assign.html
│  │  │     └─ mission_list.html
│  │  ├─ db/
│  │  │  ├─ __init__.py
│  │  │  ├─ connection.py
│  │  │  ├─ account_repository.py
│  │  │  ├─ battle_repository.py
│  │  │  ├─ demon_repository.py
│  │  │  ├─ hunter_repository.py
│  │  │  └─ mission_repository.py
│  │  ├─ service/
│  │  │  ├─ __init__.py
│  │  │  ├─ battle_service.py
│  │  │  ├─ demon_service.py
│  │  │  ├─ hunter_service.py
│  │  │  └─ mission_service.py
│  │  ├─ static/
│  │  │  └─ style.css
│  │  └─ run.py
│  └─ why/
│     └─ work.py
└─ README.md
```

- **`Backend/chainTeamProject/run.py`**: Flask 앱 실행 엔트리 포인트
- **`Backend/chainTeamProject/app/`**: Flask 앱 생성, 라우터, 템플릿(HTML) 파일
- **`Backend/chainTeamProject/db/`**: MySQL 연결 설정 및 테이블별 CRUD 로직
- **`Backend/chainTeamProject/service/`**: 비즈니스 로직 계층
- **`Backend/chainTeamProject/static/`**: CSS 등 정적 파일
- **`Backend/why/work.py`**: Flask + PyMySQL 테스트/연습용 코드

---

## 실행 방법 (요약)

1. Python 3.x와 MySQL 설치
2. 이 레포지토리 클론 후, 프로젝트 루트(README.md 있는 곳)에서:

```bash
pip install -r requirements.txt
```

3. MySQL에 `chain_db` 데이터베이스와 필요한 테이블 생성  
   - DB 접속 정보는 `Backend/chainTeamProject/db/connection.py`에서 수정 가능

4. 서버 실행

```bash
cd Backend/chainTeamProject
python run.py
```

5. 웹 브라우저에서 `http://localhost:5000` 접속
