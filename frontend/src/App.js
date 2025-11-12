import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import FilePanel from './components/FilePanel';

function App() {

  const [conversations, setConversations] = useState([ ]);

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
      />
    </div>
  );
}

export default App;
