import React, { useState } from "react";
import { MessageSquare, Plus, Loader2 } from "lucide-react";
import Message from "./Message";

function ChatArea({ conversation, onNewConv, onSendMessage }) {
  const [inputValue, setInputValue] = useState("");
  const [isQuerying, setIsQuerying] = useState(false);
  const [messages, setMessages] = useState([]);

  const handleSend = () => {
    if (!inputValue.trim() || !conversation) return;

    const userMsg = {
      id: Date.now(),
      type: "user",
      content: inputValue,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    setIsQuerying(true);

    // mock AI 답변
    setTimeout(() => {
      const aiMsg = {
        id: Date.now() + 1,
        type: "ai",
        content: "이건 mock AI 답변입니다.",
        timestamp: new Date().toLocaleTimeString(),
        videoSources: [
          { time: "00:01:23", text: "참고 영상 구간" },
        ],
      };
      setMessages((prev) => [...prev, aiMsg]);
      setIsQuerying(false);
    }, 1000);
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
                파일을 업로드하여<br />
                질의응답을 시작하세요
              </h3>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <Message key={msg.id} message={msg} />
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
              conversation.files.length === 0 ? "먼저 파일을 업로드해주세요" : ""
            }
            disabled={conversation.files.length === 0}
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