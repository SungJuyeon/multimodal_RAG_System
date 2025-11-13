import React, { useState } from 'react';
import { Upload, FileText, Video, CheckCircle, XCircle, Loader2, Database } from 'lucide-react';

function FilePanel({ conversation, onFileUpload, onRemoveFile, onCreateRAG }) {
    const [ragStatus, setRagStatus] = useState('idle'); // 'idle' | 'loading' | 'done'

    const handleFileChange = (e, type) => {
        const files = Array.from(e.target.files);
        onFileUpload(files, type);
    };

    const getFileIcon = (type) => {
        switch(type) {
        case 'document': return <FileText className="w-5 h-5 text-orange-500" />;
        case 'video': return <Video className="w-5 h-5 text-orange-500" />;
        default: return <FileText className="w-5 h-5 text-gray-500" />;
        }
    };

    const handleCreateRAG = async () => {
        setRagStatus('loading');
        await onCreateRAG(conversation.files); // 백엔드 vector 생성
        setTimeout(() => setRagStatus('done'), 800); // 시각적 효과용
    };

    if (!conversation) return null;

    return (
        <div className="w-96 bg-white border-l border-slate-200 flex flex-col">
        {/* 파일 업로드 버튼들 */}
        <div className="p-6 space-y-4">
            {/* 문서 업로드 */}
            <label className="block cursor-pointer">
            <input
                type="file"
                accept=".pdf,.doc,.docx"
                multiple
                className="hidden"
                onChange={(e) => handleFileChange(e, 'document')}
            />
            <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 hover:border-yellow-400 hover:bg-yellow-50 transition-all">
                <div className="flex items-center gap-3 mb-2">
                <FileText className="w-6 h-6 text-slate-600" />
                <div className="flex-1">
                    <div className="font-semibold text-slate-700">문서 업로드</div>
                    <div className="text-sm text-slate-500">PDF</div>
                </div>
                <Upload className="w-5 h-5 text-slate-400" />
                </div>
            </div>
            </label>

            {/* 영상 업로드 */}
            <label className="block cursor-pointer">
            <input
                type="file"
                accept=".mp4,.avi,.mov"
                multiple
                className="hidden"
                onChange={(e) => handleFileChange(e, 'video')}
            />
            <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 hover:border-yellow-400 hover:bg-yellow-50 transition-all">
                <div className="flex items-center gap-3 mb-2">
                <Video className="w-6 h-6 text-slate-600" />
                <div className="flex-1">
                    <div className="font-semibold text-slate-700">영상 업로드</div>
                    <div className="text-sm text-slate-500">MP4, AVI, MOV</div>
                </div>
                <Upload className="w-5 h-5 text-slate-400" />
                </div>
            </div>
            </label>
        </div>

        {/* 업로드된 파일이 없을 때 */}
        {conversation.files.length === 0 && (
            <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center">
                <p className="text-slate-600 font-medium mb-1">
                파일을 업로드하여
                </p>
                <p className="text-slate-500 text-sm">
                질의응답을 시작하세요
                </p>
            </div>
            </div>
        )}

        {/* 업로드된 파일 목록 */}
        {conversation.files.length > 0 && (
            <div className="flex-1 overflow-y-auto px-6 pb-6">
            <div className="space-y-3">
                {conversation.files.map(file => (
                <div
                    key={file.id}
                    className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg border border-slate-200"
                >
                    {getFileIcon(file.type)}
                    <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-slate-700 truncate">
                        {file.name}
                    </div>
                    <div className="text-xs text-slate-500">{file.size} MB</div>
                    </div>
                    {file.status === 'uploading' && (
                    <Loader2 className="w-5 h-5 text-orange-500 animate-spin" />
                    )}
                    {file.status === 'completed' && (
                    <div className="flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                        <button
                        onClick={() => onRemoveFile(file.id)}
                        className="text-slate-400 hover:text-red-500 transition-colors"
                        >
                        <XCircle className="w-5 h-5" />
                        </button>
                    </div>
                    )}
                </div>
                ))}
            </div>
            </div>
        )}
        {/* RAG 생성 버튼 */}
        {conversation.files.length > 0 && (
            <div className="p-6 border-t border-slate-200">
            <button
                disabled={ragStatus === 'loading'}
                onClick={handleCreateRAG}
                className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-medium transition-all ${
                ragStatus === 'done'
                    ? 'bg-sky-500 text-white'
                    : 'bg-gradient-to-r from-yellow-400 to-orange-400 text-white hover:shadow-lg hover:scale-105'
                }`}
            >
                {ragStatus === 'loading' && <Loader2 className="w-5 h-5 animate-spin" />}
                {ragStatus === 'done' && <CheckCircle className="w-5 h-5" />}
                {ragStatus === 'idle' && <Database className="w-5 h-5" />}
                {ragStatus === 'done' ? 'RAG 시스템 생성 완료' : ragStatus === 'loading' ? 'RAG 생성 중...' : 'RAG 시스템 만들기'}
            </button>
            </div>
        )}
        </div>
    );
}

export default FilePanel;