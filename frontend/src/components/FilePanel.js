import React, { useState } from 'react';
import { Upload, FileText, Video, CheckCircle, XCircle, Loader2, Database } from 'lucide-react';
import { uploadFile } from '../services/api';

function FilePanel({ conversation, onFileUpload, onRemoveFile, onCreateRAG }) {
    const [ragStatus, setRagStatus] = useState('idle'); // 'idle' | 'loading' | 'done'
    const [uploadingFiles, setUploadingFiles] = useState(new Set());

    const handleFileChange = async (e, type) => {
        const files = Array.from(e.target.files);
        
        for (const file of files) {
            const fileId = `${Date.now()}_${file.name}`;
            setUploadingFiles(prev => new Set(prev).add(fileId));

            try {
                // 백엔드에 파일 업로드
                const response = await uploadFile(conversation.id, file);
                
                // 프론트엔드 상태 업데이트
                onFileUpload([{
                    ...response.file,
                    id: fileId,
                    type: type
                }], type);
            } catch (error) {
                console.error('파일 업로드 실패:', error);
                alert(`파일 업로드 실패: ${file.name}`);
            } finally {
                setUploadingFiles(prev => {
                    const newSet = new Set(prev);
                    newSet.delete(fileId);
                    return newSet;
                });
            }
        }
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
        try {
            await onCreateRAG(conversation.id);
            setRagStatus('done');
        } catch (error) {
            console.error('RAG 생성 실패:', error);
            alert('RAG 시스템 생성에 실패했습니다.');
            setRagStatus('idle');
        }
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
                    {uploadingFiles.has(file.id) && (
                    <Loader2 className="w-5 h-5 text-orange-500 animate-spin" />
                    )}
                    {file.status === 'completed' && !uploadingFiles.has(file.id) && (
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
        {conversation.files.length > 0 && ragStatus !== 'done' && (
            <div className="p-6 border-t border-slate-200">
            <button
                disabled={ragStatus === 'loading'}
                onClick={handleCreateRAG}
                className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-medium transition-all ${
                ragStatus === 'loading'
                    ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-yellow-400 to-orange-400 text-white hover:shadow-lg hover:scale-105'
                }`}
            >
                {ragStatus === 'loading' && <Loader2 className="w-5 h-5 animate-spin" />}
                {ragStatus === 'idle' && <Database className="w-5 h-5" />}
                {ragStatus === 'loading' ? 'RAG 생성 중...' : 'RAG 시스템 만들기'}
            </button>
            </div>
        )}
        {ragStatus === 'done' && (
            <div className="p-6 border-t border-slate-200">
            <div className="flex items-center justify-center gap-2 px-4 py-3 bg-sky-100 rounded-xl">
                <CheckCircle className="w-5 h-5 text-sky-600" />
                <span className="font-medium text-sky-700">RAG 시스템 준비 완료</span>
            </div>
            </div>
        )}
        </div>
    );
}

export default FilePanel;