'use client';

import { useState } from 'react';
import { BatchAnalysisData, SingleExperimentResult } from '@/types';

interface BatchResultsViewProps {
    results: BatchAnalysisData;
    onGenerateReport: () => void;
    isGenerating: boolean;
}

export default function BatchResultsView({
    results,
    onGenerateReport,
    isGenerating,
}: BatchResultsViewProps) {
    const [selectedExperiment, setSelectedExperiment] = useState<number>(0);

    const currentExperiment: SingleExperimentResult | undefined =
        results.experiments[selectedExperiment];

    return (
        <div className="space-y-6">
            {/* 헤더 */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">{results.report_title}</h2>
                    <p className="text-gray-500">
                        {results.total_experiments}개 실험 분석 완료
                    </p>
                </div>
                <button
                    onClick={onGenerateReport}
                    disabled={isGenerating}
                    className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                        isGenerating
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                >
                    {isGenerating ? '리포트 생성 중...' : '전체 리포트 생성'}
                </button>
            </div>

            {/* 실험 탭 */}
            <div className="border-b border-gray-200">
                <nav className="flex gap-2 overflow-x-auto pb-2">
                    {results.experiments.map((exp, index) => (
                        <button
                            key={exp.sheet_name}
                            onClick={() => setSelectedExperiment(index)}
                            className={`px-4 py-2 rounded-t-lg font-medium whitespace-nowrap transition-colors ${
                                selectedExperiment === index
                                    ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-600'
                                    : 'text-gray-600 hover:bg-gray-100'
                            }`}
                        >
                            {exp.experiment_name}
                        </button>
                    ))}
                </nav>
            </div>

            {/* 선택된 실험 결과 */}
            {currentExperiment && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* 그래프 */}
                    <div className="bg-white border rounded-lg p-4">
                        <h3 className="text-lg font-semibold mb-4">
                            {currentExperiment.experiment_name} - 그래프
                        </h3>
                        <div className="flex justify-center">
                            <img
                                src={currentExperiment.graph.image_base64}
                                alt={`${currentExperiment.experiment_name} 그래프`}
                                className="max-w-full h-auto rounded-lg shadow"
                            />
                        </div>
                    </div>

                    {/* 통계 */}
                    <div className="bg-white border rounded-lg p-4">
                        <h3 className="text-lg font-semibold mb-4">통계 분석 결과</h3>
                        <div className="space-y-3">
                            <StatRow
                                label="기울기 (Slope)"
                                value={currentExperiment.statistics.slope.toFixed(6)}
                            />
                            <StatRow
                                label="y절편 (Intercept)"
                                value={currentExperiment.statistics.intercept.toFixed(6)}
                            />
                            <StatRow
                                label="결정계수 (R²)"
                                value={currentExperiment.statistics.r_squared.toFixed(6)}
                                highlight={currentExperiment.statistics.r_squared >= 0.95}
                            />
                            <StatRow
                                label="표준 오차"
                                value={currentExperiment.statistics.std_error.toFixed(6)}
                            />
                            <StatRow
                                label="데이터 포인트"
                                value={`${currentExperiment.statistics.data_points}개`}
                            />
                            <StatRow
                                label="X 범위"
                                value={`${currentExperiment.statistics.x_range[0].toFixed(4)} ~ ${currentExperiment.statistics.x_range[1].toFixed(4)}`}
                            />
                            <StatRow
                                label="Y 범위"
                                value={`${currentExperiment.statistics.y_range[0].toFixed(4)} ~ ${currentExperiment.statistics.y_range[1].toFixed(4)}`}
                            />
                            {currentExperiment.statistics.error_rate_percent !== null && (
                                <StatRow
                                    label="오차율"
                                    value={`${currentExperiment.statistics.error_rate_percent.toFixed(2)}%`}
                                    highlight={currentExperiment.statistics.error_rate_percent < 5}
                                    highlightColor="green"
                                />
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* 데이터 테이블 */}
            {currentExperiment && currentExperiment.data_table.length > 0 && (
                <div className="bg-white border rounded-lg p-4">
                    <h3 className="text-lg font-semibold mb-4">측정 데이터</h3>
                    <div className="overflow-x-auto max-h-64 overflow-y-auto">
                        <table className="min-w-full text-sm">
                            <thead className="bg-gray-100 sticky top-0">
                                <tr>
                                    <th className="px-4 py-2 text-left">#</th>
                                    {Object.keys(currentExperiment.data_table[0]).map((key) => (
                                        <th key={key} className="px-4 py-2 text-left">
                                            {key}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {currentExperiment.data_table.slice(0, 20).map((row, idx) => (
                                    <tr key={idx} className="border-b hover:bg-gray-50">
                                        <td className="px-4 py-2 text-gray-500">{idx + 1}</td>
                                        {Object.values(row).map((val, colIdx) => (
                                            <td key={colIdx} className="px-4 py-2">
                                                {typeof val === 'number' ? val.toFixed(4) : String(val ?? '-')}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {currentExperiment.data_table.length > 20 && (
                            <p className="text-center text-gray-500 text-sm py-2">
                                ... {currentExperiment.data_table.length - 20}개 행 더 있음
                            </p>
                        )}
                    </div>
                </div>
            )}

            {/* 매뉴얼 정보 */}
            {results.manual_info && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-yellow-800 mb-3">
                        매뉴얼 정보 (PDF에서 추출)
                    </h3>
                    <div className="space-y-3 text-sm">
                        <div>
                            <span className="font-medium">실험 목적:</span>
                            <p className="mt-1 text-gray-700">
                                {results.manual_info.experiment_purpose}
                            </p>
                        </div>
                        {results.manual_info.error_guides.length > 0 && (
                            <div>
                                <span className="font-medium">오차 원인 가이드:</span>
                                <ul className="mt-1 list-disc list-inside text-gray-700">
                                    {results.manual_info.error_guides.map((guide, idx) => (
                                        <li key={idx}>
                                            <span className="font-medium">{guide.cause}:</span>{' '}
                                            {guide.description}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

function StatRow({
    label,
    value,
    highlight = false,
    highlightColor = 'blue',
}: {
    label: string;
    value: string;
    highlight?: boolean;
    highlightColor?: 'blue' | 'green';
}) {
    const highlightClass =
        highlightColor === 'green'
            ? 'bg-green-100 text-green-700'
            : 'bg-blue-100 text-blue-700';

    return (
        <div className="flex justify-between items-center py-2 border-b border-gray-100">
            <span className="text-gray-600">{label}</span>
            <span
                className={`font-mono font-medium px-2 py-1 rounded ${
                    highlight ? highlightClass : ''
                }`}
            >
                {value}
            </span>
        </div>
    );
}
