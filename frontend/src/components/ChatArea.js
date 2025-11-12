import React, { useState } from 'react';
import { MessageSquare, Plus } from 'lucide-react';

function ChatArea({ onNewConv }) {
return (
      <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="text-center max-w-md px-8">
          <div className="w-32 h-32 bg-gradient-to-br from-yellow-400 to-orange-400 rounded-full mx-auto mb-8 flex items-center justify-center shadow-lg">
            <MessageSquare className="w-16 h-16 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-slate-800 mb-3">
            Multimodal RAG
          </h1>
          <p className="text-slate-600 mb-8 text-lg">
            이미지 있는 문서, 영상을 분석하는 질의응답 시스템
          </p>
          <button
            onClick={onNewConv}
            className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-yellow-400 to-orange-400 text-white rounded-xl font-bold text-lg hover:shadow-2xl hover:scale-105 transition-all"
          >
            <Plus className="h-5 w-5" />
            새 페이지 만들기
          </button>
        </div>
      </div>
    );
}

export default ChatArea;