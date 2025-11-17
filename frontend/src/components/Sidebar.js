import React from 'react';
import { Plus, MessageSquare, Trash2 } from 'lucide-react';

function Sidebar({ onNewConv, conversations, activeConvId, onSelectConv, onDeleteConv }) {
    const handleDelete = (e, convId) => {
        e.stopPropagation(); // 클릭 이벤트가 부모로 전파되지 않도록
        
        if (window.confirm('이 대화를 삭제하시겠습니까?')) {
            // localStorage에서 메시지도 삭제
            localStorage.removeItem(`messages_${convId}`);
            
            if (onDeleteConv) {
                onDeleteConv(convId);
            }
        }
    };
    
    return (
        <div className="w-72 bg-white border-r border-slate-200 flex flex-col">
            {/* 새 페이지 버튼 */}
            <div className='p-4 border-b border-slate-200'> {/* 새 페이지 버튼 밑에 border 추가 */}
                <button
                    onClick = {onNewConv}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-yellow-400 to-orange-400 text-white rounded-xl font-medium hover:shadow-lg hover:scale-105 transition-all"
                >
                    <Plus className="h-5 w-5" />
                    새 페이지
                </button>
            </div>

            {/* 대화 목록 */}
            <div className="flex-1 overflow-y-auto">
                {conversations.length === 0 && (
                    <div className="p-6 text-center text-slate-400 text-sm">
                        아직 생성된 대화가 없습니다
                    </div>
                )}

                {conversations.map(conv => (
                    <div
                        key={conv.id}
                        className={`relative group w-full p-4 border-b border-slate-100 hover:bg-slate-50 transition-colors ${activeConvId === conv.id ? 'bg-yellow-50 border-l-4 border-l-yellow-400' : ''}`}
                    >
                    <button
                            onClick={() => onSelectConv(conv.id)}
                            className="w-full text-left"
                        >
                            <div className="flex items-center gap-3">
                                <MessageSquare className={`w-5 h-5 flex-shrink-0 ${
                                    activeConvId === conv.id ? 'text-yellow-600' : 'text-slate-400'
                                }`} />
                                <div className="flex-1 min-w-0">
                                    <div className="font-medium text-slate-800 truncate">
                                        {conv.title || '새 대화'}
                                    </div>
                                    <div className="text-xs text-slate-500 truncate">
                                        {conv.lastActivity}
                                    </div>
                                    <div className="text-xs text-slate-400 mt-1">
                                        파일 {conv.files.length}개
                                        {conv.ragReady && ' • RAG 준비완료'}
                                    </div>
                                </div>
                            </div>
                        </button>
                        <button
                            onClick={(e) => handleDelete(e, conv.id)}
                            className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 p-2 hover:bg-red-50 rounded-lg transition-all"
                            title="대화 삭제"
                        >
                            <Trash2 className="w-4 h-4 text-slate-400 hover:text-red-500" />
                        </button>
                     </div>
                ))}
            </div>
        </div>
    );
}

export default Sidebar;