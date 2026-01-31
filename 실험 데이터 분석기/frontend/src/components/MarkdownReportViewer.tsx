'use client';

import { useState } from 'react';
import { downloadMarkdownReport } from '@/lib/api';

interface MarkdownReportViewerProps {
    markdownContent: string;
    reportTitle: string;
    onBack: () => void;
}

export default function MarkdownReportViewer({
    markdownContent,
    reportTitle,
    onBack,
}: MarkdownReportViewerProps) {
    const [viewMode, setViewMode] = useState<'preview' | 'source'>('preview');

    const handleDownload = () => {
        const filename = `${reportTitle.replace(/\s+/g, '_')}_report.md`;
        downloadMarkdownReport(markdownContent, filename);
    };

    const handleCopyToClipboard = async () => {
        try {
            await navigator.clipboard.writeText(markdownContent);
            alert('클립보드에 복사되었습니다!');
        } catch {
            alert('복사에 실패했습니다.');
        }
    };

    return (
        <div className="space-y-4">
            {/* 헤더 */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <button
                        onClick={onBack}
                        className="flex items-center gap-2 text-gray-600 hover:text-gray-800"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        뒤로
                    </button>
                    <h2 className="text-xl font-bold">{reportTitle} - 리포트</h2>
                </div>

                <div className="flex items-center gap-2">
                    {/* 뷰 모드 토글 */}
                    <div className="flex border rounded-lg overflow-hidden">
                        <button
                            onClick={() => setViewMode('preview')}
                            className={`px-4 py-2 text-sm font-medium ${
                                viewMode === 'preview'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white text-gray-600 hover:bg-gray-100'
                            }`}
                        >
                            미리보기
                        </button>
                        <button
                            onClick={() => setViewMode('source')}
                            className={`px-4 py-2 text-sm font-medium ${
                                viewMode === 'source'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white text-gray-600 hover:bg-gray-100'
                            }`}
                        >
                            소스
                        </button>
                    </div>

                    {/* 복사 버튼 */}
                    <button
                        onClick={handleCopyToClipboard}
                        className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                        복사
                    </button>

                    {/* 다운로드 버튼 */}
                    <button
                        onClick={handleDownload}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        다운로드 (.md)
                    </button>
                </div>
            </div>

            {/* 컨텐츠 */}
            <div className="border rounded-lg bg-white">
                {viewMode === 'preview' ? (
                    <div className="p-6 prose prose-sm max-w-none overflow-auto max-h-[70vh]">
                        <MarkdownPreview content={markdownContent} />
                    </div>
                ) : (
                    <div className="relative">
                        <pre className="p-6 text-sm font-mono bg-gray-50 overflow-auto max-h-[70vh] whitespace-pre-wrap">
                            {markdownContent}
                        </pre>
                    </div>
                )}
            </div>

            {/* 안내 메시지 */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
                <strong>팁:</strong> 다운로드한 .md 파일은 VS Code, Typora, Notion 등에서 열어볼 수 있습니다.
                이미지는 Base64로 임베딩되어 있어 별도 파일 없이 표시됩니다.
            </div>
        </div>
    );
}

/**
 * 간단한 마크다운 미리보기 컴포넌트
 * 실제 프로덕션에서는 react-markdown 등의 라이브러리 사용 권장
 */
function MarkdownPreview({ content }: { content: string }) {
    // 간단한 마크다운 렌더링 (헤더, 볼드, 이미지 등)
    const renderMarkdown = (text: string) => {
        const lines = text.split('\n');
        const elements: JSX.Element[] = [];
        let inCodeBlock = false;
        let codeContent: string[] = [];

        lines.forEach((line, idx) => {
            // 코드 블록
            if (line.startsWith('```')) {
                if (inCodeBlock) {
                    elements.push(
                        <pre key={idx} className="bg-gray-100 p-4 rounded-lg overflow-x-auto my-4 text-sm">
                            <code>{codeContent.join('\n')}</code>
                        </pre>
                    );
                    codeContent = [];
                }
                inCodeBlock = !inCodeBlock;
                return;
            }

            if (inCodeBlock) {
                codeContent.push(line);
                return;
            }

            // H1
            if (line.startsWith('# ')) {
                elements.push(
                    <h1 key={idx} className="text-3xl font-bold mt-8 mb-4 border-b pb-2">
                        {line.slice(2)}
                    </h1>
                );
                return;
            }

            // H2
            if (line.startsWith('## ')) {
                elements.push(
                    <h2 key={idx} className="text-2xl font-bold mt-6 mb-3">
                        {line.slice(3)}
                    </h2>
                );
                return;
            }

            // H3
            if (line.startsWith('### ')) {
                elements.push(
                    <h3 key={idx} className="text-xl font-semibold mt-4 mb-2">
                        {line.slice(4)}
                    </h3>
                );
                return;
            }

            // H4
            if (line.startsWith('#### ')) {
                elements.push(
                    <h4 key={idx} className="text-lg font-semibold mt-3 mb-2">
                        {line.slice(5)}
                    </h4>
                );
                return;
            }

            // 이미지 (Base64 포함)
            const imageMatch = line.match(/!\[([^\]]*)\]\(([^)]+)\)/);
            if (imageMatch) {
                elements.push(
                    <figure key={idx} className="my-4">
                        <img
                            src={imageMatch[2]}
                            alt={imageMatch[1]}
                            className="max-w-full h-auto rounded-lg shadow mx-auto"
                        />
                        {imageMatch[1] && (
                            <figcaption className="text-center text-sm text-gray-500 mt-2">
                                {imageMatch[1]}
                            </figcaption>
                        )}
                    </figure>
                );
                return;
            }

            // 테이블 (간단한 처리)
            if (line.startsWith('|')) {
                elements.push(
                    <div key={idx} className="overflow-x-auto my-2">
                        <code className="text-sm">{line}</code>
                    </div>
                );
                return;
            }

            // 수평선
            if (line === '---' || line === '***') {
                elements.push(<hr key={idx} className="my-6 border-gray-300" />);
                return;
            }

            // 리스트 아이템
            if (line.startsWith('- ') || line.startsWith('* ')) {
                elements.push(
                    <li key={idx} className="ml-4 my-1">
                        {renderInlineMarkdown(line.slice(2))}
                    </li>
                );
                return;
            }

            // 빈 줄
            if (line.trim() === '') {
                elements.push(<div key={idx} className="h-2" />);
                return;
            }

            // 일반 텍스트
            elements.push(
                <p key={idx} className="my-2 leading-relaxed">
                    {renderInlineMarkdown(line)}
                </p>
            );
        });

        return elements;
    };

    // 인라인 마크다운 처리 (볼드, 이탤릭, 코드)
    const renderInlineMarkdown = (text: string): React.ReactNode => {
        // 볼드 **text**
        let result: React.ReactNode = text;

        // 간단한 볼드 처리
        const boldParts = text.split(/\*\*([^*]+)\*\*/g);
        if (boldParts.length > 1) {
            return boldParts.map((part, idx) =>
                idx % 2 === 1 ? <strong key={idx}>{part}</strong> : part
            );
        }

        return result;
    };

    return <div>{renderMarkdown(content)}</div>;
}
