'use client';

import { useState, useEffect } from 'react';
import { SheetInfo, ExperimentConfig } from '@/types';

interface SheetConfigEditorProps {
    sheets: SheetInfo[];
    onConfigChange: (configs: ExperimentConfig[]) => void;
}

export default function SheetConfigEditor({
    sheets,
    onConfigChange,
}: SheetConfigEditorProps) {
    const [configs, setConfigs] = useState<ExperimentConfig[]>([]);

    // 시트 정보가 변경되면 초기 설정 생성
    useEffect(() => {
        const initialConfigs: ExperimentConfig[] = sheets.map((sheet) => ({
            sheet_name: sheet.sheet_name,
            experiment_name: sheet.sheet_name,
            x_column: sheet.columns[0] || '',
            y_column: sheet.columns[1] || '',
            theoretical_slope: undefined,
        }));
        setConfigs(initialConfigs);
        onConfigChange(initialConfigs);
    }, [sheets]);

    const updateConfig = (index: number, field: keyof ExperimentConfig, value: string | number | undefined) => {
        const newConfigs = [...configs];
        newConfigs[index] = {
            ...newConfigs[index],
            [field]: value,
        };
        setConfigs(newConfigs);
        onConfigChange(newConfigs);
    };

    const toggleSheet = (index: number, enabled: boolean) => {
        if (enabled) {
            // 시트 활성화
            const sheet = sheets[index];
            const newConfig: ExperimentConfig = {
                sheet_name: sheet.sheet_name,
                experiment_name: sheet.sheet_name,
                x_column: sheet.columns[0] || '',
                y_column: sheet.columns[1] || '',
            };
            const newConfigs = [...configs];
            newConfigs[index] = newConfig;
            setConfigs(newConfigs);
            onConfigChange(newConfigs.filter((c) => c.sheet_name));
        } else {
            // 시트 비활성화 (빈 객체로 대체)
            const newConfigs = [...configs];
            newConfigs[index] = { sheet_name: '', experiment_name: '', x_column: '', y_column: '' };
            setConfigs(newConfigs);
            onConfigChange(newConfigs.filter((c) => c.sheet_name));
        }
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">시트별 실험 설정</h3>
                <span className="text-sm text-gray-500">
                    {configs.filter((c) => c.sheet_name).length}/{sheets.length} 시트 선택됨
                </span>
            </div>

            {sheets.map((sheet, index) => {
                const config = configs[index];
                const isEnabled = config && config.sheet_name !== '';

                return (
                    <div
                        key={sheet.sheet_name}
                        className={`border rounded-lg p-4 transition-colors ${
                            isEnabled ? 'border-blue-300 bg-blue-50' : 'border-gray-200 bg-gray-50'
                        }`}
                    >
                        {/* 시트 헤더 */}
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-3">
                                <input
                                    type="checkbox"
                                    checked={isEnabled}
                                    onChange={(e) => toggleSheet(index, e.target.checked)}
                                    className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium">{sheet.sheet_name}</span>
                                    <span className="ml-2 text-sm text-gray-500">
                                        ({sheet.row_count}행, {sheet.columns.length}열)
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* 설정 폼 */}
                        {isEnabled && (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-3">
                                {/* 실험 이름 */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        실험 이름
                                    </label>
                                    <input
                                        type="text"
                                        value={config.experiment_name}
                                        onChange={(e) =>
                                            updateConfig(index, 'experiment_name', e.target.value)
                                        }
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="실험 이름"
                                    />
                                </div>

                                {/* X축 열 */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        X축 열
                                    </label>
                                    <select
                                        value={config.x_column}
                                        onChange={(e) =>
                                            updateConfig(index, 'x_column', e.target.value)
                                        }
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        {sheet.columns.map((col) => (
                                            <option key={col} value={col}>
                                                {col}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Y축 열 */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Y축 열
                                    </label>
                                    <select
                                        value={config.y_column}
                                        onChange={(e) =>
                                            updateConfig(index, 'y_column', e.target.value)
                                        }
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        {sheet.columns.map((col) => (
                                            <option key={col} value={col}>
                                                {col}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* 이론적 기울기 (선택) */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        이론적 기울기 <span className="text-gray-400">(선택)</span>
                                    </label>
                                    <input
                                        type="number"
                                        step="any"
                                        value={config.theoretical_slope ?? ''}
                                        onChange={(e) =>
                                            updateConfig(
                                                index,
                                                'theoretical_slope',
                                                e.target.value ? parseFloat(e.target.value) : undefined
                                            )
                                        }
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="오차율 계산용"
                                    />
                                </div>
                            </div>
                        )}

                        {/* 샘플 데이터 미리보기 */}
                        {isEnabled && sheet.sample_data.length > 0 && (
                            <div className="mt-4">
                                <details className="text-sm">
                                    <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                                        샘플 데이터 미리보기
                                    </summary>
                                    <div className="mt-2 overflow-x-auto">
                                        <table className="min-w-full text-xs border">
                                            <thead className="bg-gray-100">
                                                <tr>
                                                    {sheet.columns.map((col) => (
                                                        <th
                                                            key={col}
                                                            className="px-2 py-1 border text-left"
                                                        >
                                                            {col}
                                                        </th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {sheet.sample_data.slice(0, 3).map((row, rowIdx) => (
                                                    <tr key={rowIdx}>
                                                        {sheet.columns.map((col) => (
                                                            <td key={col} className="px-2 py-1 border">
                                                                {String(row[col] ?? '-')}
                                                            </td>
                                                        ))}
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </details>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
