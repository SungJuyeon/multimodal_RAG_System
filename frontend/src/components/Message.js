import React from 'react';
import clsx from 'clsx';

function Message({ message }) {
  const defaultMessage = {
    type: 'ai',
    content: '이건 mock 답변입니다. 디자인 확인용입니다.',
    timestamp: new Date().toLocaleTimeString(),
    videoSources: [
      { time: '00:01:23', text: '이 부분 참고' },
      { time: '00:02:10', text: '다른 참고' }
    ]
  };

  const msg = message || defaultMessage;
  const isUser = msg.type === 'user';

  return (
    <div className={clsx("flex w-full mb-4", isUser ? "justify-end" : "justify-start")}>
      <div className={clsx(
        "max-w-[70%] p-4 rounded-2xl break-words",
        isUser ? "bg-[#FDE4A3] text-slate-900 rounded-br-none" : "bg-[#FFF7E0] text-slate-900 rounded-bl-none"
      )}>
        <div className="text-sm">{msg.content}</div>

        {!isUser && msg.videoSources && msg.videoSources.length > 0 && (
          <div className="mt-3 space-y-2">
            <div className="flex items-center gap-2">
                🔎 영상 출처
            </div>
            {msg.videoSources.map((source, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <div className="bg-yellow-300 text-yellow-1000 text-xs px-3 py-2 rounded-xl font-medium">
                 {source.time}
                </div>
                <div className="text-xs text-slate-700">{source.text}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Message;