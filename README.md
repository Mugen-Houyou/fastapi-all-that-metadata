# fastapi-all-that-metadata

기본적인 FastAPI 웹 서비스 레포지토리 (A basic FastAPI web service repository)

## 개요 (Overview)

이 프로젝트는 FastAPI를 사용하여 이미지 파일의 EXIF 메타데이터를 분석하고 편집할 수 있는 웹 서비스를 제공합니다.

This project is a FastAPI-based web service for analysing and editing EXIF metadata from image files.

## 기능 (Features)

- ✅ FastAPI 프레임워크 기반
- ✅ 자동 API 문서화 (Swagger UI & ReDoc)
- ✅ Pydantic을 사용한 데이터 검증
- ✅ RESTful API 엔드포인트
- ✅ Health check 엔드포인트
- ✅ CRUD 작업 예제

## 설치 (Installation)

### Prerequisites

- Python 3.10 이상; 3.12 권장 (Python 3.10 or higher; 3.12 recommended)

### 설치 단계 (Installation Steps)

1. 레포지토리 클론 (Clone the repository):
```bash
git clone https://github.com/Mugen-Houyou/fastapi-all-that-metadata.git
cd fastapi-all-that-metadata
```

2. 가상 환경 생성 및 활성화 (Create and activate virtual environment):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. 의존성 설치 (Install dependencies):
```bash
pip install -r requirements.txt
```

## 사용법 (Usage)

### 서버 실행 (Running the Server)

다음 명령어로 서버를 실행할 수 있습니다:

```bash
python main.py
```

또는 uvicorn을 직접 사용:

```bash
uvicorn main:app --reload
```

서버는 기본적으로 `http://localhost:8000`에서 실행됩니다. 웹 브라우저에서 `http://localhost:8000`을 열면 이미지 업로드 및 분석 UI를 사용할 수 있습니다.

### API 문서 (API Documentation)

서버 실행 후, 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 엔드포인트 (API Endpoints)

### Root
- `GET /` - index.html 반환

### Health Check
- `GET /health` - 서비스 상태 확인

### EXIF
- `POST /api/exif` - 업로드한 이미지의 EXIF 메타데이터 분석
- `POST /api/exif/edit` - EXIF 값을 수정하거나 제거한 새로운 이미지를 반환

### 예제 요청 (Example Requests)

#### EXIF 분석 (Analyze EXIF)
```bash
curl -X POST "http://localhost:8000/api/exif" \
  -F "file=@sample.jpg"
```

#### EXIF 편집 (Edit EXIF)
```bash
curl -X POST "http://localhost:8000/api/exif/edit" \
  -F "file=@sample.jpg" \
  -F 'updates={"Artist": "All-that-EXIF"}' \
  -F 'removals=["UserComment"]'
```

## 프로젝트 구조 (Project Structure)

```
fastapi-all-that-metadata/
├── main.py              # FastAPI application
├── metadata_service.py  # 메타데이터 분석/편집 유틸리티
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project metadata
├── static/              # Front-end assets (HTML/JS/CSS)
└── README.md            # This file
```

## 개발 (Development)

### 의존성 추가 (Adding Dependencies)

새로운 패키지를 추가하려면:

```bash
pip install <package-name>
pip freeze > requirements.txt
```

## 라이선스 (License)

This project is open source and available under the MIT License.

## 기여 (Contributing)

기여는 언제나 환영합니다! (Contributions are always welcome!)

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request