# PythonAnywhere 배포 가이드

## 1단계: GitHub에 프로젝트 업로드

### 로컬에서 Git 초기화 및 업로드

```bash
# Git 초기화 (아직 안 했다면)
git init

# .gitignore가 이미 생성되어 있으므로 다음 파일들이 제외됩니다
# - __pycache__/
# - .venv/
# - staticfiles/
# - db.sqlite3
# - media/

# 파일 추가
git add .

# 커밋
git commit -m "Initial commit for PythonAnywhere deployment"

# GitHub에 새 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## 2단계: PythonAnywhere 설정

### A. PythonAnywhere 대시보드에서

1. **Files 탭**에서 `mysite/` 폴더 생성 (또는 기존 폴더 사용)
2. **Web 탭**에서 새 웹 앱 생성
3. **Consoles 탭**에서 Bash 콘솔 열기

### B. Bash 콘솔에서 실행할 명령어

```bash
# 1. 프로젝트 디렉토리로 이동
cd ~/YOUR_PROJECT_DIRECTORY

# 2. 가상환경 생성 (Python 3.10 권장)
python3.10 -m venv venv

# 3. 가상환경 활성화
source venv/bin/activate

# 4. GitHub에서 프로젝트 클론 (또는 직접 업로드)
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git .
# 또는 Files 탭에서 직접 업로드

# 5. 필요한 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt

# 6. 정적 파일 수집
python manage.py collectstatic --noinput

# 7. 데이터베이스 마이그레이션
python manage.py migrate

# 8. 슈퍼유저 생성 (선택사항)
python manage.py createsuperuser
```

## 3단계: PythonAnywhere Web 앱 설정

### Web 탭에서 설정

1. **Source code:** `/home/YOUR_USERNAME/YOUR_PROJECT_DIRECTORY`
2. **Working directory:** `/home/YOUR_USERNAME/YOUR_PROJECT_DIRECTORY`
3. **WSGI configuration file:** 클릭하여 수정

### WSGI 설정 파일 수정

```python
import os
import sys

# 프로젝트 경로 추가
path = '/home/YOUR_USERNAME/YOUR_PROJECT_DIRECTORY'
if path not in sys.path:
    sys.path.insert(0, path)

# 가상환경 활성화
activate_this = '/home/YOUR_USERNAME/YOUR_PROJECT_DIRECTORY/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Django 설정
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Static files 설정

**Static files** 섹션에서:
- URL: `/static/`
- Directory: `/home/YOUR_USERNAME/YOUR_PROJECT_DIRECTORY/staticfiles`

### Media files 설정 (선택사항)

**Static files** 섹션에 추가:
- URL: `/media/`
- Directory: `/home/YOUR_USERNAME/YOUR_PROJECT_DIRECTORY/media`

## 4단계: 환경 변수 설정 (선택사항)

### SECRET_KEY 보안 강화

`config/settings.py`에서:

```python
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')
```

Bash 콘솔에서:
```bash
export SECRET_KEY='your-secret-key-here'
```

또는 `.env` 파일 사용 (python-dotenv 설치 필요)

## 5단계: 웹 앱 재로드

Web 탭에서 **Reload** 버튼 클릭

## 6단계: 확인

브라우저에서 `https://YOUR_USERNAME.pythonanywhere.com` 접속하여 확인

---

## 주의사항

1. **DEBUG = False**로 설정되어 있으므로 에러 발생 시 상세 정보가 표시되지 않습니다.
2. **ALLOWED_HOSTS = ["*"]**는 개발용입니다. 실제 도메인을 사용할 경우 해당 도메인만 추가하세요.
3. **SECRET_KEY**는 반드시 변경하세요.
4. **데이터베이스**는 PythonAnywhere의 MySQL을 사용하거나 SQLite를 계속 사용할 수 있습니다.

## 문제 해결

- **500 에러:** Web 탭의 Error log 확인
- **정적 파일 미표시:** `collectstatic` 실행 확인 및 Static files 경로 확인
- **마이그레이션 오류:** `python manage.py migrate` 재실행

