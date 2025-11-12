import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';


function App() {

  const [conversations, setConversations] = useState([
    {
      id: 1,
      title: '새 대화',
      files: [],
      messages: [],
      lastActivity: '방금 전'
    }
  ]);

  const [activeConvId, setActiveConvId] = useState(1);

  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar 
        conversations={conversations}
        activeConvId={activeConvId}
        onSelectConv={setActiveConvId}
        onNewConv={() => {/* 새 대화 생성 로직 */}}
      />
    </div>
  );
}

export default App;
