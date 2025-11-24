const API_BASE_URL = "http://localhost:8000/api";

export const uploadFile = async (convId, file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/conversations/${convId}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("파일 업로드 실패");
  }

  return response.json();
};

export const createRAG = async (convId) => {
  const response = await fetch(`${API_BASE_URL}/conversations/${convId}/create-rag`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("RAG 생성 실패");
  }

  return response.json();
};

export const sendQuery = async (convId, query) => {
  const response = await fetch(`${API_BASE_URL}/conversations/${convId}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error("질의 처리 실패");
  }

  return response.json();
};

export const getConversationStatus = async (convId) => {
  const response = await fetch(`${API_BASE_URL}/conversations/${convId}/status`);
  
  if (!response.ok) {
    throw new Error("상태 조회 실패");
  }

  return response.json();
};

export const deleteFile = async (convId, fileId) => {
  const response = await fetch(`${API_BASE_URL}/conversations/${convId}/files/${fileId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("파일 삭제 실패");
  }

  return response.json();
};