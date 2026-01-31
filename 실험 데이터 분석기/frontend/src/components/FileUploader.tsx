'use client';

import { useState, useCallback } from 'react';
import { analyzeData, detectColumns } from '@/lib/api';
import { AnalysisData } from '@/types';

interface FileUploaderProps {
    onAnalysisComplete: (result: AnalysisData) => void;
    onError: (message: string) => void;
}

export default function FileUploader({ onAnalysisComplete, onError }: FileUploaderProps) {
    const [file, setFile] = useState<File | null>(null);
    const [title, setTitle] = useState('');
    const [xColumn, setXColumn] = useState('');
    const [yColumn, setYColumn] = useState('');
    const [theoreticalSlope, setTheoreticalSlope] = useState('');
    const [columns, setColumns] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isDetecting, setIsDetecting] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const [manualMode, setManualMode] = useState(false);

    // 파일 선택 시 열 정보 감지
    const handleFileChange = useCallback(async (selectedFile: File) => {
        setFile(selectedFile);
        setIsDetecting(true);
        setColumns([]);
        setXColumn('');
        setYColumn('');

        try {
            const result = await detectColumns(selectedFile);
            console.log('Column detection result:', result);

            if (result.success && result.columns && Array.isArray(result.columns)) {
                const colNames = result.columns.map((c: { name: string }) => c.name);
                console.log('Detected columns:', colNames);
                setColumns(colNames);
                // 첫 두 열을 기본 선택
                if (colNames.length >= 2) {
                    setXColumn(colNames[0]);
                    setYColumn(colNames[1]);
                }
                setManualMode(false);
            } else {
                console.log('No columns detected, switching to manual mode');
                setManualMode(true);
            }
        } catch (err) {
            console.error('열 감지 실패:', err);
            setManualMode(true);
        } finally {
            setIsDetecting(false);
        }
    }, []);

    // 드래그 앤 드롭
    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            handleFileChange(droppedFile);
        }
    }, [handleFileChange]);

    // 분석 시작
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!file || !title || !xColumn || !yColumn) {
            onError('모든 필드를 입력해주세요.');
            return;
        }

        setIsLoading(true);
        try {
            const result = await analyzeData(
                file,
                title,
                xColumn,
                yColumn,
                theoreticalSlope ? parseFloat(theoreticalSlope) : undefined
            );

            if (result.success && result.data) {
                onAnalysisComplete(result.data);
            } else {
                onError(result.message || '분석에 실패했습니다.');
            }
        } catch (err) {
            onError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            {/* 파일 업로드 영역 */}
            <div
                onDrop={handleDrop}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                className={`
          border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-all duration-200
          ${isDragging ? 'border-blue-500 bg-blue-500/20' : 'border-white/30 hover:border-blue-400'}
          ${file ? 'bg-green-500/20 border-green-400' : ''}
        `}
                onClick={() => document.getElementById('file-input')?.click()}
            >
                <input
                    id="file-input"
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    className="hidden"
                    onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
                />

                {isDetecting ? (
                    <div className="text-blue-300">
                        <svg className="animate-spin w-12 h-12 mx-auto mb-2" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        <p className="font-medium">열 정보 감지 중...</p>
                    </div>
                ) : file ? (
                    <div className="text-green-300">
                        <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <p className="font-medium">{file.name}</p>
                        <p className="text-sm text-white/50 mt-1">클릭하여 다른 파일 선택</p>
                        {columns.length > 0 && (
                            <p className="text-xs text-green-400 mt-2">
                                {columns.length}개 열 감지됨: {columns.join(', ')}
                            </p>
                        )}
                    </div>
                ) : (
                    <div className="text-white/70">
                        <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <p className="font-medium">파일을 드래그하거나 클릭하여 업로드</p>
                        <p className="text-sm mt-1">CSV, Excel 파일 지원</p>
                    </div>
                )}
            </div>

            {/* 실험 제목 */}
            <div>
                <label className="block text-sm font-medium text-white/80 mb-1">
                    실험 제목
                </label>
                <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="예: RC 회로 시정수 측정 실험"
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>

            {/* X축/Y축 선택 */}
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium text-white/80 mb-1">
                        X축 열
                    </label>
                    {manualMode || columns.length === 0 ? (
                        <input
                            type="text"
                            value={xColumn}
                            onChange={(e) => setXColumn(e.target.value)}
                            placeholder="예: time"
                            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500"
                        />
                    ) : (
                        <select
                            value={xColumn}
                            onChange={(e) => setXColumn(e.target.value)}
                            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="" className="bg-slate-800">선택하세요</option>
                            {columns.map((col) => (
                                <option key={col} value={col} className="bg-slate-800">{col}</option>
                            ))}
                        </select>
                    )}
                </div>
                <div>
                    <label className="block text-sm font-medium text-white/80 mb-1">
                        Y축 열
                    </label>
                    {manualMode || columns.length === 0 ? (
                        <input
                            type="text"
                            value={yColumn}
                            onChange={(e) => setYColumn(e.target.value)}
                            placeholder="예: voltage"
                            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500"
                        />
                    ) : (
                        <select
                            value={yColumn}
                            onChange={(e) => setYColumn(e.target.value)}
                            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="" className="bg-slate-800">선택하세요</option>
                            {columns.map((col) => (
                                <option key={col} value={col} className="bg-slate-800">{col}</option>
                            ))}
                        </select>
                    )}
                </div>
            </div>

            {/* 수동 입력 모드 토글 */}
            {columns.length > 0 && (
                <button
                    type="button"
                    onClick={() => setManualMode(!manualMode)}
                    className="text-sm text-white/50 hover:text-white/80 underline"
                >
                    {manualMode ? '감지된 열에서 선택' : '열 이름 직접 입력'}
                </button>
            )}

            {/* 이론적 기울기 (선택) */}
            <div>
                <label className="block text-sm font-medium text-white/80 mb-1">
                    이론적 기울기 <span className="text-white/40">(선택사항 - 오차율 계산용)</span>
                </label>
                <input
                    type="number"
                    step="any"
                    value={theoreticalSlope}
                    onChange={(e) => setTheoreticalSlope(e.target.value)}
                    placeholder="예: 10.0"
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500"
                />
            </div>

            {/* 분석 버튼 */}
            <button
                type="submit"
                disabled={isLoading || !file || !title || !xColumn || !yColumn}
                className={`
          w-full py-3 px-6 rounded-lg font-semibold text-white
          transition-all duration-200
          ${isLoading || !file || !title || !xColumn || !yColumn
                        ? 'bg-gray-500/50 cursor-not-allowed'
                        : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl'
                    }
        `}
            >
                {isLoading ? (
                    <span className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        분석 중...
                    </span>
                ) : (
                    '🔬 분석 시작'
                )}
            </button>
        </form>
    );
}
