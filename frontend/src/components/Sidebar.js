import React from 'react';
import { Plus, MessageSquare } from 'lucide-react';

function Sidebar({ onNewCon, conversations, activeConvId, onSelectConv }) {
    return (
        <div className="w-72 bg-white border-r border-slate-200 flex flex-col">
            {/* 새 페이지 버튼 */}
            <div className='p-4 border-b border-slate-200'>
                <button
                    onClick = {onNewCon}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-yellow-400 to-orange-400 text-white rounded-xl font-medium hover:shadow-lg hover:scale-105 transition-all"
                >
                    <Plus className="h-5 w-5" />
                    새 페이지
                </button>
            </div>

            {/* 대화 목록 */}
            <div className="flex-1 overflow-y-auto">
                {conversations.map(conv => (
                    <button
                        key={conv.id}
                        onClick={() => onSelectConv(conv.id)}
                        className={`w-full p-4 border-b border-slate-100 hover:bg-slate-50 transition-colors text-left ${activeConvId === conv.id ? 'bg-yellow-50 border-l-4 border-l-yellow-400' : ''}`}
                    >
                        <div className="flex items-center gap-3">
                            <MessageSquare className={`w-5 h-5 ${
                                activeConvId === conv.id ? 'text-yellow-600' : 'text-slate-400'
                            }`} />
                            <div className="flex-1">
                                <div className="font-medium text-slate-800">
                                    {conv.title || '새 대화'}
                                </div>
                                <div className="text-sm text-slate-500 truncate">
                                    {conv.lastActivity}
                                </div>
                            </div>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
}

export default Sidebar;