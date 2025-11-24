from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import conversations

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(conversations.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Multimodal RAG API"}

if __name__ == "__main__":
	import uvicorn
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)