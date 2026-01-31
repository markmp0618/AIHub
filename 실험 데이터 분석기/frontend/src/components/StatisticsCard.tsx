'use client';

import { StatisticsResult } from '@/types';

interface StatisticsCardProps {
    statistics: StatisticsResult;
}

export default function StatisticsCard({ statistics }: StatisticsCardProps) {
    const formatNumber = (num: number, decimals: number = 4) => {
        return num.toFixed(decimals);
    };

    const getR2Quality = (r2: number): { label: string; color: string } => {
        if (r2 >= 0.99) return { label: '매우 우수', color: 'text-green-600' };
        if (r2 >= 0.95) return { label: '우수', color: 'text-green-500' };
        if (r2 >= 0.90) return { label: '양호', color: 'text-yellow-600' };
        return { label: '개선 필요', color: 'text-red-500' };
    };

    const r2Quality = getR2Quality(statistics.r_squared);

    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                통계 분석 결과
            </h3>

            <div className="grid grid-cols-2 gap-4">
                {/* 기울기 */}
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                    <p className="text-sm text-blue-600 font-medium">기울기 (Slope)</p>
                    <p className="text-2xl font-bold text-blue-800">{formatNumber(statistics.slope)}</p>
                </div>

                {/* y절편 */}
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
                    <p className="text-sm text-purple-600 font-medium">y절편 (Intercept)</p>
                    <p className="text-2xl font-bold text-purple-800">{formatNumber(statistics.intercept)}</p>
                </div>

                {/* R² */}
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
                    <p className="text-sm text-green-600 font-medium">결정계수 (R²)</p>
                    <p className="text-2xl font-bold text-green-800">{formatNumber(statistics.r_squared)}</p>
                    <p className={`text-xs mt-1 ${r2Quality.color}`}>{r2Quality.label}</p>
                </div>

                {/* 표준 오차 */}
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4">
                    <p className="text-sm text-orange-600 font-medium">표준 오차</p>
                    <p className="text-2xl font-bold text-orange-800">{formatNumber(statistics.std_error)}</p>
                </div>

                {/* 오차율 (있는 경우) */}
                {statistics.error_rate_percent !== null && (
                    <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4">
                        <p className="text-sm text-red-600 font-medium">오차율</p>
                        <p className="text-2xl font-bold text-red-800">{statistics.error_rate_percent}%</p>
                    </div>
                )}

                {/* 데이터 포인트 수 */}
                <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-4">
                    <p className="text-sm text-gray-600 font-medium">데이터 포인트</p>
                    <p className="text-2xl font-bold text-gray-800">{statistics.data_points}개</p>
                </div>
            </div>

            {/* 회귀 방정식 */}
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">회귀 방정식</p>
                <p className="text-lg font-mono font-semibold text-gray-800">
                    y = {formatNumber(statistics.slope)}x {statistics.intercept >= 0 ? '+' : ''} {formatNumber(statistics.intercept)}
                </p>
            </div>
        </div>
    );
}
