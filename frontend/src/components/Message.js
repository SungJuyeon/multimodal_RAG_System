import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import clsx from 'clsx';
import { ChevronDown, ChevronUp, Image as ImageIcon } from 'lucide-react';

function Message({ message }) {
  const msg = message;
  const isUser = msg.type === 'user';
  const [showImages, setShowImages] = useState(true);

  return (
    <div className={clsx("flex w-full mb-4", isUser ? "justify-end" : "justify-start")}>
      <div className={clsx(
        "max-w-[70%] p-4 rounded-2xl break-words",
        isUser ? "bg-[#FDE4A3] text-slate-900 rounded-br-none" : "bg-[#FFF7E0] text-slate-900 rounded-bl-none"
      )}>
        {/* 답변 텍스트 */}
        <div className="text-sm">
          {isUser ? msg.content : <ReactMarkdown>{msg.content}</ReactMarkdown>}
        </div>

        {/* 이미지 렌더링 */}
        {!isUser && msg.images && msg.images.length > 0 && (
          <div className="mt-4 border-t border-slate-200 pt-4">
            <button
              onClick={() => setShowImages(!showImages)}
              className="flex items-center gap-2 text-sm font-medium text-slate-700 hover:text-slate-900 mb-3"
            >
              <ImageIcon className="w-4 h-4" />
              <span>참고 이미지 ({msg.images.length}개)</span>
              {showImages ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            
            {showImages && (
              <div className="grid grid-cols-1 gap-3">
                {msg.images.map((img, idx) => (
                  <div key={idx} className="relative group">
                    <img
                      src={`data:image/jpeg;base64,${img}`}
                      alt={`참고 이미지 ${idx + 1}`}
                      className="w-full rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => {
                        // 이미지 클릭 시 새 창에서 크게 보기
                        const newWindow = window.open();
                        newWindow.document.write(`<img src="data:image/jpeg;base64,${img}" style="max-width:100%;height:auto;" />`);
                      }}
                    />
                    <div className="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
                      이미지 {idx + 1}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Message;