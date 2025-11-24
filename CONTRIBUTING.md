### 설치 및 실행 방법
---
**1) Repository Clone**
```
git clone https://github.com/your-id/multimodal-rag.git
cd multimodal-rag
```
<br>

**2) Environment Setup .env 파일을 생성하고 API 키를 입력하세요.**
```
OPENAI_API_KEY=your_api_key_here
```
<br>

**3) Backend Setup**
```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
<br>

**4) Frontend Setup**
```
cd frontend
npm install
npm run dev
```
<br>

**5) Docker 실행(옵션)**
```
docker compose up --build
```
<br>
