## 기술 스택 및 설치 라이브러리

- **언어**: Python 3.10.3
- **웹 프레임워크**: Flask
- **DB**: MySQL (`chain_db` 데이터베이스 사용)
- **Python 라이브러리 (pip로 설치 필요)**  
- **flask**: 웹 서버 및 라우팅, 템플릿 렌더링 등에 사용  
- **pymysql**: Python에서 MySQL 데이터베이스에 접속하기 위해 사용

## 주요 폴더
- **`Backend/chainTeamProject/run.py`**: Flask 앱 실행 엔트리 포인트
- **`Backend/chainTeamProject/app/`**: Flask 앱 생성, 라우터, 템플릿(HTML) 파일
- **`Backend/chainTeamProject/db/`**: MySQL 연결 설정 및 테이블별 CRUD 로직
- **`Backend/chainTeamProject/service/`**: 비즈니스 로직 계층
- **`Backend/chainTeamProject/static/`**: CSS 등 정적 파일
- **`Backend/why/work.py`**: Flask + PyMySQL 테스트/연습용 코드

---

## 실행 방법 (요약)
1. MySQL에 `chain_db.sql' 파일 사용
   - DB 접속 정보는 `Backend/chainTeamProject/db/connection.py`에서 mysql 비밀 번호

2. 서버 실행
```bash
cd Backend/chainTeamProject
python run.py
```

3. 웹 브라우저에서 `http://localhost:5000` 접속

