## 📘 Multimodal RAG System
PDF · Image · Video 기반의 멀티모달 RAG 시스템 <br>
<p align="center">
  <img src="https://img.shields.io/badge/Framework-FastAPI-009688?style=flat-square"/>
  <img src="https://img.shields.io/badge/Backend-Python-00000F?style=flat-square"/>
  <img src="https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square"/>
  <img src="https://img.shields.io/badge/Styling-TailwindCSS-38bdf8?style=flat-square"/>
  <img src="https://img.shields.io/badge/VectorDB-FAISS-005571?style=flat-square"/>
  <img src="https://img.shields.io/badge/Deployed-Docker-0db7ed?style=flat-square"/>
</p>

## 📖 프로젝트 개요
이 프로젝트는 멀티모달 데이터를 처리하는 RAG(Retrieval-Augmented Generation) 시스템을 처음부터 직접 구현하는 것을 목표로 한다.<br>
텍스트뿐 아니라 이미지·표가 포함된 PDF, 영상 프레임, 이미지 자체를 분석하여 검색하는 구조를 구축했다.<br>
PDF/Image/Video → 임베딩 → 벡터DB → 검색 → LLM 응답까지 전체 파이프라인 구성<br>

## ⭐️ 주요 기능
**1) 멀티모달 데이터 처리<br>**
	•	PDF (텍스트 + 이미지 + 표)<br>
	•	이미지 파일<br>
	•	영상 → 프레임 → 시각 임베딩<br>

**2) 전체 RAG 파이프라인 구현<br>**
	•	데이터 전처리<br>
	•	임베딩 추출<br>
	•	벡터 DB 저장/검색<br>
	•	LLM 기반 질의응답<br>

**3) VideoRAG 프로토타입 구현<br>**
	•	영상 프레임 추출<br>
	•	각 프레임 임베딩 후 검색<br>
	•	쿼리에 따라 관련 프레임 기반 답변 생성<br>

**4) UI/UX 구현<br>**
	•	Figma 기반 와이어프레임 제작<br>
	•	React + Tailwind CSS로 실제 인터페이스 개발<br>

**5) API 서버<br>**
	•	FastAPI 기반 API 라우팅<br>
	•	업로드 → 처리 → 검색 → 응답까지 end-to-end 작업<br>

**6) Docker 기반 실행 환경<br>**
	•	프론트/백엔드 컨테이너화<br>
	•	로컬 및 서버 환경 통일<br>
<br>

## Data Pipeline (PDF & Video)

```mermaid
graph TD
    subgraph "Input Sources"
        PDF[PDF 문서]
        Video[비디오 파일]
    end

    subgraph "Preprocessing Engine"
        PDF -->|Unstructured| Text[텍스트 분리]
        PDF -->|Unstructured| Table[표 추출]
        PDF -->|Unstructured| Img[이미지 추출]
        
        Video -->|OpenCV| Frame[Key Frame 추출]
        Video -->|FFmpeg| Audio[오디오 추출]
    end

    subgraph "Understanding & Embedding"
        Text -->|GPT-4o| TextSum[텍스트 요약]
        Table -->|GPT-4o| TableSum[표 요약]
        Img -->|CLIP + GPT-4o| ImgDesc[이미지 분석]
        
        Frame & Audio -->|GPT-4o| VideoSum[영상 구간 분석]
    end

    subgraph "Vector Store (ChromaDB)"
        TextSum --> VectorDB
        TableSum --> VectorDB
        ImgDesc --> VectorDB
        VideoSum --> VectorDB
    end

    VectorDB -->|Retrieval| LLM[Generate Answer]
```



## 시연

**•	PDF 업로드**
<img width="1254" height="821" alt="image" src="https://github.com/user-attachments/assets/8287e5cd-08ad-421e-9441-cd0dc848c42b" />

**•	사용자 질의**
<img width="995" height="789" alt="image (1)" src="https://github.com/user-attachments/assets/b525cce5-5f2b-433f-9cb2-e5a3d633ed0a" />

**•	문서 질의응답과 이미지 출처**
<img width="1049" height="798" alt="image (2)" src="https://github.com/user-attachments/assets/8083bc0d-d365-45eb-a7fe-219abc342709" />

**•	영상 업로드**
<img width="1163" height="852" alt="image (3)" src="https://github.com/user-attachments/assets/4fd934c8-0351-4e26-a29e-208aaa117714" />

**•	영상 질의응답과 출처**
<img width="709" height="501" alt="image" src="https://github.com/user-attachments/assets/a42fec5d-eaac-4c6a-8572-f009e53eeaf9" />
