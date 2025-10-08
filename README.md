# fastapi-all-that-metadata

기본적인 FastAPI 웹 서비스 레포지토리 (A basic FastAPI web service repository)

## 개요 (Overview)

이 프로젝트는 FastAPI를 사용한 기본적인 RESTful API 웹 서비스입니다. CRUD(Create, Read, Update, Delete) 작업을 수행할 수 있는 예제 엔드포인트를 포함하고 있습니다.

This project is a basic RESTful API web service using FastAPI. It includes example endpoints for performing CRUD (Create, Read, Update, Delete) operations.

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

서버는 기본적으로 `http://localhost:8000`에서 실행됩니다.

### API 문서 (API Documentation)

서버 실행 후, 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 엔드포인트 (API Endpoints)

### Root
- `GET /` - index.html 반환

### Health Check
- `GET /health` - 서비스 상태 확인

### Items (CRUD Operations)
- `GET /items` - 모든 아이템 조회
- `GET /items/{item_id}` - 특정 아이템 조회
- `POST /items` - 새 아이템 생성
- `PUT /items/{item_id}` - 아이템 수정
- `DELETE /items/{item_id}` - 아이템 삭제

### 예제 요청 (Example Requests)

#### 아이템 생성 (Create Item)
```bash
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Item",
    "description": "This is an example item",
    "price": 29.99
  }'
```

#### 모든 아이템 조회 (Get All Items)
```bash
curl -X GET "http://localhost:8000/items"
```

#### 특정 아이템 조회 (Get Item by ID)
```bash
curl -X GET "http://localhost:8000/items/1"
```

#### 아이템 수정 (Update Item)
```bash
curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Item",
    "price": 39.99
  }'
```

#### 아이템 삭제 (Delete Item)
```bash
curl -X DELETE "http://localhost:8000/items/1"
```

## 프로젝트 구조 (Project Structure)

```
fastapi-all-that-metadata/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project metadata
├── .gitignore          # Git ignore file
└── README.md           # This file
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