import React, { useState, useEffect } from "react";
import { MessageSquare, Plus, Loader2, Film } from "lucide-react";
import Message from "./Message";
import { sendQuery } from "../services/api";

function ChatArea({ conversation, onNewConv, onSendMessage }) {
  const [inputValue, setInputValue] = useState("");
  const [isQuerying, setIsQuerying] = useState(false);
  const [messages, setMessages] = useState(() => {
    if (!conversation) return [];
    const saved = localStorage.getItem(`messages_${conversation.id}`);
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    if (conversation) {
      const saved = localStorage.getItem(`messages_${conversation.id}`);
      setMessages(saved ? JSON.parse(saved) : []);
    } else {
      setMessages([]);
    }
  }, [conversation?.id]);

  useEffect(() => {
    if (conversation) {
      localStorage.setItem(`messages_${conversation.id}`, JSON.stringify(messages));
    }
  }, [messages, conversation?.id]);

  const handleSend = async () => {
    if (!inputValue.trim() || !conversation) return;

    const userMsg = {
      id: Date.now(),
      type: "user",
      content: inputValue,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    const query = inputValue;
    setInputValue("");
    setIsQuerying(true);

    try {
      const response = await sendQuery(conversation.id, query);
      
      console.log('서버 응답:', response);
      
      const aiMsg = {
        id: Date.now() + 1,
        type: "ai",
        content: response.answer || "답변을 생성하지 못했습니다.",
        timestamp: new Date().toLocaleTimeString(),
        videoSources: response.video_sources || response.sources || [],
        images: response.images || [],
      };
      
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      console.error('질의 처리 실패:', error);
      
      const errorMsg = {
        id: Date.now() + 1,
        type: "ai",
        content: "죄송합니다. 답변 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        timestamp: new Date().toLocaleTimeString(),
        videoSources: [],
        images: [],
      };
      
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsQuerying(false);
    }
  };

  if (!conversation) {
    return (
      <div className="flex-1 flex items-center justify-center bg-white">
        <div className="text-center max-w-md px-8">
          <div className="w-40 h-40 bg-gradient-to-br from-yellow-100 to-orange-100 rounded-full mx-auto mb-8 flex items-center justify-center">
            <MessageSquare className="w-20 h-20 text-orange-400" strokeWidth={2} />
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-4">
            Multimodal RAG
          </h1>
          <p className="text-slate-600 mb-2 text-lg">
            문서, 영상을 먼저 업로드하고 무엇이든 물어보세요
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

  return (
    <div className="flex-1 flex flex-col bg-white">
      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-24 h-24 bg-slate-100 rounded-full mx-auto mb-6 flex items-center justify-center">
                <MessageSquare className="w-12 h-12 text-slate-400" />
              </div>
              <h3 className="text-2xl font-bold text-slate-800 mb-3">
                {conversation.ragReady 
                  ? "질문을 입력하세요" 
                  : "파일을 업로드하고\nRAG 시스템을 만들어주세요"}
              </h3>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id}>
            {/* 메시지 */}
            <Message message={msg} />
            
            {/* 영상 타임라인 */}
            {msg.type === 'ai' && msg.videoSources && msg.videoSources.length > 0 && (
              <div className="mt-2 mb-4">
                <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-4 border border-yellow-200 max-w-[70%]">
                  <div className="flex items-center gap-2 mb-3">
                    <Film className="w-4 h-4 text-orange-600" />
                    <span className="text-sm font-semibold text-slate-800">영상 출처</span>
                  </div>
                  <div className="space-y-2">
                    {msg.videoSources.map((source, idx) => (
                      <div key={idx} className="flex items-start gap-3 bg-white/80 p-3 rounded-lg hover:bg-white transition-colors">
                        <div className="bg-gradient-to-r from-yellow-400 to-orange-400 text-white text-xs font-bold px-3 py-1.5 rounded-lg flex-shrink-0 shadow-sm">
                          {source.time}
                        </div>
                        <div className="text-xs text-slate-700 flex-1 leading-relaxed">
                          {source.text}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
        
        {isQuerying && (
          <div className="flex justify-start">
            <div className="bg-slate-100 rounded-2xl px-5 py-3">
              <div className="flex items-center gap-2 text-slate-600">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">답변 생성 중...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 입력 영역 */}
      <div className="border-t border-slate-200 bg-white p-6">
        <div className="flex gap-3 items-center max-w-4xl mx-auto">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            placeholder={
              !conversation.ragReady 
                ? "먼저 RAG 시스템을 만들어주세요" 
                : "질문을 입력하세요..."
            }
            disabled={!conversation.ragReady}
            className="flex-1 px-6 py-4 border-2 border-slate-200 rounded-full focus:outline-none focus:border-orange-400 disabled:bg-slate-50 disabled:text-slate-400 transition-all text-slate-700"
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || conversation.files.length === 0 || isQuerying}
            className="w-14 h-14 bg-gradient-to-r from-yellow-400 to-orange-400 text-white rounded-full hover:shadow-lg hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all flex items-center justify-center flex-shrink-0"
          >
            <MessageSquare className="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatArea;