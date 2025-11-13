import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import FilePanel from './components/FilePanel';

function App() {

  const [conversations, setConversations] = useState([ ]);
  const [ragReady, setRagReady] = useState(false);
  const [activeConvId, setActiveConvId] = useState(1);
  const activeConversation = conversations.find(c => c.id === activeConvId);

  const createNewConversation = () => {
    const newConv = {
      id: Date.now(),
      title: '새 대화',
      files: [],
      messages: [],
      lastActivity: '방금 전'
    };
    setConversations(prev => [newConv, ...prev]);
    setActiveConvId(newConv.id);
    setRagReady(false);
  };

  const handleFileUpload = (files, type) => {
    setConversations(prev =>
      prev.map(conv => {
        if (conv.id === activeConvId) {
          const newFiles = files.map(file => ({
            id: Date.now() + Math.random(),
            name: file.name,
            size: (file.size / 1024 / 1024).toFixed(2),
            type,
            status: 'completed',
          }));
          return { ...conv, files: [...conv.files, ...newFiles] };
        }
        return conv;
      })
    );
    setRagReady(false);
  };

  const handleRemoveFile = (fileId) => {
    setConversations(prev =>
      prev.map(conv => {
        if (conv.id === activeConvId) {
          return {
            ...conv,
            files: conv.files.filter(f => f.id !== fileId),
          };
        }
        return conv;
      })
    );
    setRagReady(false);
  };

  const handleCreateRAG = async (files) => {
    setRagReady(false);
    // 프론트엔드 시뮬레이션: 1초 뒤 RAG 생성 완료
    setTimeout(() => setRagReady(true), 1000);
  };

  const handleSendMessage = (text) => {
    if (!activeConvId) return;

    setConversations(prev =>
      prev.map(conv =>
        conv.id === activeConvId
          ? {
              ...conv,
              messages: [
                ...conv.messages,
                { id: Date.now(), sender: 'user', text }
              ],
              lastActivity: '방금 전'
            }
          : conv
      )
    );
  };

  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar 
        conversations={conversations}
        activeConvId={activeConvId}
        onSelectConv={setActiveConvId}
        onNewConv={createNewConversation}
      />

      <ChatArea 
        conversation={activeConversation}
        onNewConv={createNewConversation}
        onSendMessage={handleSendMessage}
        ragReady={ragReady}
      />

      {activeConvId && (
        <FilePanel 
          conversation={activeConversation}
          onFileUpload={handleFileUpload}
          onRemoveFile={handleRemoveFile}
          onCreateRAG={handleCreateRAG}
        />
      )}
    </div>
  );
}

export default App;
