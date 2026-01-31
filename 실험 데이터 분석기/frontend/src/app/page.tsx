'use client';

import { useState } from 'react';
import FileUploader from '@/components/FileUploader';
import StatisticsCard from '@/components/StatisticsCard';
import MultiFileUploader from '@/components/MultiFileUploader';
import SheetConfigEditor from '@/components/SheetConfigEditor';
import BatchResultsView from '@/components/BatchResultsView';
import MarkdownReportViewer from '@/components/MarkdownReportViewer';
import {
  AnalysisData,
  SheetInfo,
  ExperimentConfig,
  ExperimentManualInfo,
  BatchAnalysisData,
  AnalysisStep,
} from '@/types';
import { generateDiscussion, analyzeBatch, generateFullReport } from '@/lib/api';

type AppMode = 'single' | 'multi';

export default function Home() {
  // 앱 모드
  const [appMode, setAppMode] = useState<AppMode | null>(null);

  // ========== 단일 분석 모드 상태 ==========
  const [analysisResult, setAnalysisResult] = useState<AnalysisData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [discussion, setDiscussion] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [experimentTitle, setExperimentTitle] = useState('');

  // ========== 멀티 분석 모드 상태 ==========
  const [currentStep, setCurrentStep] = useState<AnalysisStep>('upload');
  const [excelFile, setExcelFile] = useState<File | null>(null);
  const [sheets, setSheets] = useState<SheetInfo[]>([]);
  const [experimentConfigs, setExperimentConfigs] = useState<ExperimentConfig[]>([]);
  const [manualInfo, setManualInfo] = useState<ExperimentManualInfo | null>(null);
  const [batchResults, setBatchResults] = useState<BatchAnalysisData | null>(null);
  const [reportTitle, setReportTitle] = useState('');
  const [markdownReport, setMarkdownReport] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // ========== 단일 분석 핸들러 ==========
  const handleAnalysisComplete = (result: AnalysisData) => {
    setAnalysisResult(result);
    setError(null);
    setDiscussion(null);
  };

  const handleError = (message: string) => {
    setError(message);
  };

  const handleReset = () => {
    setAppMode(null);
    // 단일 모드 리셋
    setAnalysisResult(null);
    setError(null);
    setDiscussion(null);
    setExperimentTitle('');
    // 멀티 모드 리셋
    setCurrentStep('upload');
    setExcelFile(null);
    setSheets([]);
    setExperimentConfigs([]);
    setManualInfo(null);
    setBatchResults(null);
    setReportTitle('');
    setMarkdownReport(null);
  };

  const handleGenerateDiscussion = async () => {
    if (!analysisResult) return;

    setIsGenerating(true);
    setError(null);

    try {
      const result = await generateDiscussion(
        experimentTitle || '실험 분석',
        analysisResult.statistics
      );

      if (result.success && result.discussion) {
        setDiscussion(result.discussion);
      } else {
        setError(result.message || '고찰 생성에 실패했습니다.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '고찰 생성 중 오류가 발생했습니다.');
    } finally {
      setIsGenerating(false);
    }
  };

  // ========== 멀티 분석 핸들러 ==========
  const handleExcelUploaded = (file: File, detectedSheets: SheetInfo[]) => {
    setExcelFile(file);
    setSheets(detectedSheets);
    setError(null);
  };

  const handleManualExtracted = (info: ExperimentManualInfo) => {
    setManualInfo(info);
  };

  const handleConfigChange = (configs: ExperimentConfig[]) => {
    setExperimentConfigs(configs);
  };

  const handleStartBatchAnalysis = async () => {
    if (!excelFile || experimentConfigs.length === 0) {
      setError('Excel 파일과 실험 설정이 필요합니다.');
      return;
    }

    if (!reportTitle.trim()) {
      setError('리포트 제목을 입력해주세요.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setCurrentStep('analyzing');

    try {
      const response = await analyzeBatch(excelFile, {
        experiments: experimentConfigs.filter((c) => c.sheet_name),
        report_title: reportTitle,
        manual_info: manualInfo || undefined,
      });

      if (response.success && response.data) {
        setBatchResults(response.data);
        setCurrentStep('results');
      } else {
        setError(response.message || '배치 분석에 실패했습니다.');
        setCurrentStep('configure');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '배치 분석 중 오류가 발생했습니다.');
      setCurrentStep('configure');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!batchResults) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await generateFullReport({
        batch_id: batchResults.batch_id,
        report_title: batchResults.report_title,
        experiments: batchResults.experiments,
        manual_info: batchResults.manual_info || undefined,
      });

      if (response.success && response.markdown_content) {
        setMarkdownReport(response.markdown_content);
        setCurrentStep('report');
      } else {
        setError(response.message || '리포트 생성에 실패했습니다.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '리포트 생성 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const canProceedToConfigure = excelFile !== null && sheets.length > 0;
  const canStartAnalysis = experimentConfigs.filter((c) => c.sheet_name).length > 0 && reportTitle.trim() !== '';

  // ========== 렌더링 ==========
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* 헤더 */}
      <header className="border-b border-white/10 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white flex items-center">
              <span className="text-3xl mr-2">📊</span>
              LabReportAI
            </h1>
            {(appMode !== null || analysisResult) && (
              <button
                onClick={handleReset}
                className="px-4 py-2 text-sm text-white/70 hover:text-white border border-white/20 rounded-lg hover:bg-white/10 transition"
              >
                처음으로
              </button>
            )}
          </div>
          <p className="text-white/60 text-sm mt-1">
            실험 데이터 분석 및 AI 리포트 자동 생성기
          </p>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* 에러 메시지 */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200">
            <p className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </p>
          </div>
        )}

        {/* ========== 모드 선택 화면 ========== */}
        {appMode === null && !analysisResult && (
          <div className="max-w-2xl mx-auto space-y-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-white mb-2">분석 모드 선택</h2>
              <p className="text-white/60">원하는 분석 방식을 선택하세요</p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* 단일 분석 모드 */}
              <button
                onClick={() => setAppMode('single')}
                className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 hover:border-blue-400 hover:bg-white/15 transition-all text-left"
              >
                <div className="text-4xl mb-4">📈</div>
                <h3 className="text-xl font-bold text-white mb-2">단일 실험 분석</h3>
                <p className="text-white/60 text-sm">
                  하나의 CSV/Excel 파일을 업로드하여 빠르게 분석합니다.
                </p>
                <ul className="mt-4 text-white/50 text-xs space-y-1">
                  <li>• 단일 데이터셋 분석</li>
                  <li>• 빠른 결과 확인</li>
                  <li>• AI 고찰 생성</li>
                </ul>
              </button>

              {/* 멀티 실험 모드 */}
              <button
                onClick={() => setAppMode('multi')}
                className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 hover:border-purple-400 hover:bg-white/15 transition-all text-left"
              >
                <div className="text-4xl mb-4">📚</div>
                <h3 className="text-xl font-bold text-white mb-2">멀티 실험 리포트</h3>
                <p className="text-white/60 text-sm">
                  여러 시트의 데이터를 한 번에 분석하고 전체 리포트를 생성합니다.
                </p>
                <ul className="mt-4 text-white/50 text-xs space-y-1">
                  <li>• 멀티시트 Excel 지원</li>
                  <li>• PDF 매뉴얼 자동 분석</li>
                  <li>• 마크다운 리포트 생성</li>
                </ul>
              </button>
            </div>
          </div>
        )}

        {/* ========== 단일 분석 모드 ========== */}
        {appMode === 'single' && !analysisResult && (
          <div className="max-w-xl mx-auto">
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-6 text-center">
                실험 데이터 업로드
              </h2>
              <FileUploader
                onAnalysisComplete={handleAnalysisComplete}
                onError={handleError}
              />
            </div>
            <div className="mt-8 text-center text-white/50 text-sm">
              <p>CSV 또는 Excel 파일을 업로드하면</p>
              <p>자동으로 선형 회귀 분석과 그래프를 생성합니다.</p>
            </div>
          </div>
        )}

        {/* 단일 분석 결과 */}
        {appMode === 'single' && analysisResult && (
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-white">분석 완료!</h2>
              <p className="text-white/60 mt-1">분석 ID: {analysisResult.analysis_id}</p>
            </div>

            <div className="grid lg:grid-cols-2 gap-8">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">회귀 분석 그래프</h3>
                <img
                  src={analysisResult.graph.image_base64}
                  alt="분석 그래프"
                  className="w-full rounded-lg"
                />
              </div>
              <StatisticsCard statistics={analysisResult.statistics} />
            </div>

            {/* AI 고찰 생성 */}
            <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 backdrop-blur-md rounded-xl p-6 border border-purple-500/30">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <span className="text-2xl mr-2">🤖</span>
                AI 고찰 생성
              </h3>
              {!discussion ? (
                <div className="space-y-4">
                  <input
                    type="text"
                    value={experimentTitle}
                    onChange={(e) => setExperimentTitle(e.target.value)}
                    placeholder="실험 제목 (선택)"
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40"
                  />
                  <button
                    onClick={handleGenerateDiscussion}
                    disabled={isGenerating}
                    className={`w-full py-3 rounded-lg font-semibold text-white transition ${
                      isGenerating ? 'bg-gray-500/50' : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
                    }`}
                  >
                    {isGenerating ? 'AI가 고찰을 작성 중...' : '✨ AI 고찰 생성하기'}
                  </button>
                </div>
              ) : (
                <div className="bg-white rounded-xl p-6 prose prose-sm max-w-none">
                  <div dangerouslySetInnerHTML={{ __html: discussion.replace(/\n/g, '<br/>') }} />
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========== 멀티 실험 모드 ========== */}
        {appMode === 'multi' && (
          <div className="space-y-6">
            {/* 스텝 인디케이터 */}
            <div className="flex items-center justify-center gap-4 mb-8">
              {['upload', 'configure', 'results', 'report'].map((step, idx) => {
                const stepLabels: Record<string, string> = {
                  upload: '1. 업로드',
                  configure: '2. 설정',
                  results: '3. 결과',
                  report: '4. 리포트',
                };
                const isActive = currentStep === step;
                const isPast = ['upload', 'configure', 'results', 'report'].indexOf(currentStep) > idx;

                return (
                  <div key={step} className="flex items-center">
                    <div
                      className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                        isActive
                          ? 'bg-blue-600 text-white'
                          : isPast
                          ? 'bg-green-600 text-white'
                          : 'bg-white/20 text-white/50'
                      }`}
                    >
                      {stepLabels[step]}
                    </div>
                    {idx < 3 && <div className="w-8 h-0.5 bg-white/20 mx-2" />}
                  </div>
                );
              })}
            </div>

            {/* Step 1: 업로드 */}
            {currentStep === 'upload' && (
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
                <h2 className="text-xl font-semibold text-white mb-6 text-center">
                  파일 업로드
                </h2>
                <MultiFileUploader
                  onExcelUploaded={handleExcelUploaded}
                  onManualExtracted={handleManualExtracted}
                  onError={handleError}
                />

                {canProceedToConfigure && (
                  <div className="mt-6 text-center">
                    <p className="text-green-400 mb-4">
                      ✓ {sheets.length}개 시트 감지됨
                    </p>
                    <button
                      onClick={() => setCurrentStep('configure')}
                      className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition"
                    >
                      다음: 실험 설정 →
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Step 2: 설정 */}
            {currentStep === 'configure' && (
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
                <div className="mb-6">
                  <label className="block text-white font-medium mb-2">리포트 제목 *</label>
                  <input
                    type="text"
                    value={reportTitle}
                    onChange={(e) => setReportTitle(e.target.value)}
                    placeholder="예: 물리학 실험 보고서 - RC 회로"
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="bg-white rounded-xl p-6">
                  <SheetConfigEditor
                    sheets={sheets}
                    onConfigChange={handleConfigChange}
                  />
                </div>

                <div className="mt-6 flex justify-between">
                  <button
                    onClick={() => setCurrentStep('upload')}
                    className="px-6 py-3 border border-white/30 text-white rounded-lg hover:bg-white/10 transition"
                  >
                    ← 이전
                  </button>
                  <button
                    onClick={handleStartBatchAnalysis}
                    disabled={!canStartAnalysis || isLoading}
                    className={`px-8 py-3 rounded-lg font-semibold transition ${
                      canStartAnalysis && !isLoading
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'bg-gray-500 text-gray-300 cursor-not-allowed'
                    }`}
                  >
                    {isLoading ? '분석 중...' : '분석 시작 →'}
                  </button>
                </div>
              </div>
            )}

            {/* Step 3: 분석 중 */}
            {currentStep === 'analyzing' && (
              <div className="text-center py-20">
                <div className="animate-spin w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-6" />
                <h2 className="text-2xl font-bold text-white mb-2">데이터 분석 중...</h2>
                <p className="text-white/60">잠시만 기다려주세요</p>
              </div>
            )}

            {/* Step 4: 결과 */}
            {currentStep === 'results' && batchResults && (
              <div className="bg-white rounded-2xl p-8">
                <BatchResultsView
                  results={batchResults}
                  onGenerateReport={handleGenerateReport}
                  isGenerating={isLoading}
                />
              </div>
            )}

            {/* Step 5: 리포트 */}
            {currentStep === 'report' && markdownReport && batchResults && (
              <div className="bg-white rounded-2xl p-8">
                <MarkdownReportViewer
                  markdownContent={markdownReport}
                  reportTitle={batchResults.report_title}
                  onBack={() => setCurrentStep('results')}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
