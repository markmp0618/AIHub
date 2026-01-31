'use client';

import ChatbotInput from './ChatbotInput';

export default function HeroSection() {
  return (
    <section className="flex flex-col items-center justify-center min-h-screen px-6 py-20">
      <div className="max-w-5xl w-full space-y-12 text-center">
        {/* Main Title */}
        <h1 className="text-7xl md:text-8xl lg:text-9xl font-medium tracking-tight text-black" style={{ fontFamily: "'Pretendard Variable', sans-serif" }}>
          AIHub
        </h1>

        {/* Subtitle */}
        <p className="text-base md:text-lg lg:text-xl text-black font-normal max-w-3xl mx-auto leading-relaxed" style={{ fontFamily: "'Pretendard Variable', sans-serif" }}>
          AI가 모두의 기본기가 되는 시대를 만듭니다. 복잡한 도구들 사이에서 길을 잃지 않도록, 가장 쉬운 시작점을 제공합니다
        </p>

        {/* Chatbot Input */}
        <div className="pt-8">
          <ChatbotInput />
        </div>

        {/* Optional: Helper text */}
        <p className="text-sm text-black mt-6" style={{ fontFamily: "'Pretendard Variable', sans-serif" }}>
          무엇이든 물어보세요. AIHub이 실행 가능한 솔루션을 제공합니다.
        </p>
      </div>
    </section>
  );
}
