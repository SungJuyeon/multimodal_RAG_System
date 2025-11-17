import React, { useState, useEffect } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import FilePanel from './components/FilePanel';
import { createRAG, deleteFile } from './services/api';

function App() {

  const [conversations, setConversations] = useState(() => {
    const saved = localStorage.getItem('conversations');
    return saved ? JSON.parse(saved) : [];
  });
  const [activeConvId, setActiveConvId] = useState(() => {
    return localStorage.getItem('activeConvId') || null;
  });

  // conversations 변경 시 localStorage에 저장
  useEffect(() => {
    localStorage.setItem('conversations', JSON.stringify(conversations));
  }, [conversations]);

  // activeConvId 변경 시 localStorage에 저장
  useEffect(() => {
    if (activeConvId) {
      localStorage.setItem('activeConvId', activeConvId);
    }
  }, [activeConvId]);

  const handleNewConv = () => {
    const newConv = {
      id: `conv_${Date.now()}`,
      title: `대화 ${conversations.length + 1}`,
      lastActivity: new Date().toLocaleString('ko-KR'),
      files: [],
      ragReady: false
    };
    
    setConversations(prev => [...prev, newConv]);
    setActiveConvId(newConv.id);
  };

  const handleSelectConv = (convId) => {
    setActiveConvId(convId);
  };

  const handleDeleteConv = (convId) => {
    setConversations(prev => prev.filter(c => c.id !== convId));
    
    // 삭제된 대화가 현재 활성 대화였다면 초기화
    if (activeConvId === convId) {
      setActiveConvId(null);
    }
    
    // localStorage에서 메시지 삭제
    localStorage.removeItem(`messages_${convId}`);
  };

  const handleFileUpload = (files) => {
    setConversations(prev =>
      prev.map(conv =>
        conv.id === activeConvId
          ? { 
              ...conv, 
              files: [...conv.files, ...files],
              lastActivity: new Date().toLocaleString('ko-KR')
            }
          : conv
      )
    );
  };

  const handleRemoveFile = async (fileId) => {
    try {
      await deleteFile(activeConvId, fileId);
      
      setConversations(prev =>
        prev.map(conv =>
          conv.id === activeConvId
            ? { 
                ...conv, 
                files: conv.files.filter(f => f.id !== fileId),
                ragReady: false,
                lastActivity: new Date().toLocaleString('ko-KR')
              }
            : conv
        )
      );
    } catch (error) {
      console.error('파일 삭제 실패:', error);
      alert('파일 삭제에 실패했습니다.');
    }
  };

  const handleCreateRAG = async (convId) => {
    try {
      await createRAG(convId);
      
      setConversations(prev =>
        prev.map(conv =>
          conv.id === convId
            ? { ...conv, ragReady: true, lastActivity: new Date().toLocaleString('ko-KR') }
            : conv
        )
      );
    } catch (error) {
      console.error('RAG 생성 실패:', error);
      throw error;
    }
  };
  
  const activeConv = conversations.find(c => c.id === activeConvId);

  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar 
        conversations={conversations}
        activeConvId={activeConvId}
        onSelectConv={handleSelectConv}
        onNewConv={handleNewConv}
        onDeleteConv={handleDeleteConv}
      />

      <ChatArea 
        conversation={activeConv}
        onNewConv={handleNewConv}
      />

      {activeConvId && (
        <FilePanel 
          conversation={activeConv}
          onFileUpload={handleFileUpload}
          onRemoveFile={handleRemoveFile}
          onCreateRAG={handleCreateRAG}
        />
      )}
    </div>
  );
}

export default App;
