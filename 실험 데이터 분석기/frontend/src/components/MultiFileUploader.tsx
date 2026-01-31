'use client';

import { useState, useCallback } from 'react';
import { SheetInfo, ExperimentManualInfo } from '@/types';
import { detectExcelSheets, extractManualFromPdf } from '@/lib/api';

interface MultiFileUploaderProps {
    onExcelUploaded: (file: File, sheets: SheetInfo[]) => void;
    onManualExtracted: (manualInfo: ExperimentManualInfo) => void;
    onError: (message: string) => void;
}

export default function MultiFileUploader({
    onExcelUploaded,
    onManualExtracted,
    onError,
}: MultiFileUploaderProps) {
    const [excelFile, setExcelFile] = useState<File | null>(null);
    const [pdfFile, setPdfFile] = useState<File | null>(null);
    const [isLoadingExcel, setIsLoadingExcel] = useState(false);
    const [isLoadingPdf, setIsLoadingPdf] = useState(false);
    const [extractedManual, setExtractedManual] = useState<ExperimentManualInfo | null>(null);

    const handleExcelChange = useCallback(
        async (e: React.ChangeEvent<HTMLInputElement>) => {
            const file = e.target.files?.[0];
            if (!file) return;

            const extension = file.name.split('.').pop()?.toLowerCase();
            if (!['xlsx', 'xls'].includes(extension || '')) {
                onError('Excel 파일(.xlsx, .xls)만 업로드 가능합니다.');
                return;
            }

            setExcelFile(file);
            setIsLoadingExcel(true);

            try {
                const response = await detectExcelSheets(file);
                if (response.success) {
                    onExcelUploaded(file, response.sheets);
                } else {
                    onError(response.message || '시트 감지에 실패했습니다.');
                }
            } catch (err) {
                onError(err instanceof Error ? err.message : '시트 감지 중 오류가 발생했습니다.');
            } finally {
                setIsLoadingExcel(false);
            }
        },
        [onExcelUploaded, onError]
    );

    const handlePdfChange = useCallback(
        async (e: React.ChangeEvent<HTMLInputElement>) => {
            const file = e.target.files?.[0];
            if (!file) return;

            if (!file.name.toLowerCase().endsWith('.pdf')) {
                onError('PDF 파일(.pdf)만 업로드 가능합니다.');
                return;
            }

            setPdfFile(file);
            setIsLoadingPdf(true);

            try {
                const response = await extractManualFromPdf(file);
                if (response.success && response.data) {
                    setExtractedManual(response.data);
                    onManualExtracted(response.data);
                } else {
                    onError(response.message || '매뉴얼 추출에 실패했습니다.');
                }
            } catch (err) {
                onError(err instanceof Error ? err.message : 'PDF 추출 중 오류가 발생했습니다.');
            } finally {
                setIsLoadingPdf(false);
            }
        },
        [onManualExtracted, onError]
    );

    return (
        <div className="space-y-6">
            {/* Excel 파일 업로드 */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-400 transition-colors">
                <div className="flex flex-col items-center">
                    <svg
                        className="w-12 h-12 text-green-500 mb-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                    </svg>
                    <h3 className="text-lg font-semibold mb-2">
                        Excel 파일 업로드 <span className="text-red-500">*</span>
                    </h3>
                    <p className="text-sm text-gray-500 mb-4">
                        멀티시트 Excel 파일 (.xlsx, .xls)
                    </p>

                    <input
                        type="file"
                        accept=".xlsx,.xls"
                        onChange={handleExcelChange}
                        className="hidden"
                        id="excel-upload"
                        disabled={isLoadingExcel}
                    />
                    <label
                        htmlFor="excel-upload"
                        className={`px-4 py-2 rounded-md cursor-pointer transition-colors ${
                            isLoadingExcel
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-green-500 text-white hover:bg-green-600'
                        }`}
                    >
                        {isLoadingExcel ? '분석 중...' : '파일 선택'}
                    </label>

                    {excelFile && (
                        <p className="mt-3 text-sm text-green-600 font-medium">
                            {excelFile.name}
                        </p>
                    )}
                </div>
            </div>

            {/* PDF 매뉴얼 업로드 (선택) */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-400 transition-colors">
                <div className="flex flex-col items-center">
                    <svg
                        className="w-12 h-12 text-red-500 mb-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                        />
                    </svg>
                    <h3 className="text-lg font-semibold mb-2">
                        PDF 매뉴얼 업로드 <span className="text-gray-400">(선택)</span>
                    </h3>
                    <p className="text-sm text-gray-500 mb-4">
                        실험 매뉴얼 PDF - AI가 오차 가이드를 자동 추출합니다
                    </p>

                    <input
                        type="file"
                        accept=".pdf"
                        onChange={handlePdfChange}
                        className="hidden"
                        id="pdf-upload"
                        disabled={isLoadingPdf}
                    />
                    <label
                        htmlFor="pdf-upload"
                        className={`px-4 py-2 rounded-md cursor-pointer transition-colors ${
                            isLoadingPdf
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-red-500 text-white hover:bg-red-600'
                        }`}
                    >
                        {isLoadingPdf ? '추출 중...' : '파일 선택'}
                    </label>

                    {pdfFile && (
                        <p className="mt-3 text-sm text-red-600 font-medium">
                            {pdfFile.name}
                        </p>
                    )}
                </div>
            </div>

            {/* 추출된 매뉴얼 정보 미리보기 */}
            {extractedManual && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-800 mb-2">
                        추출된 매뉴얼 정보
                    </h4>
                    <div className="text-sm text-gray-700 space-y-2">
                        <p>
                            <span className="font-medium">실험 목적:</span>{' '}
                            {extractedManual.experiment_purpose.substring(0, 100)}...
                        </p>
                        <p>
                            <span className="font-medium">오차 가이드:</span>{' '}
                            {extractedManual.error_guides.length}개 항목
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}
