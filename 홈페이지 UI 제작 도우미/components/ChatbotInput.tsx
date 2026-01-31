'use client';

import { useState } from 'react';

export default function ChatbotInput() {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      console.log('User input:', input);
      // Here you would typically handle the chatbot interaction
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
      <div className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="AIHub에게 물어보세요..."
          className="w-full px-6 py-4 text-base rounded-2xl
                     bg-white/80 backdrop-blur-md
                     border border-gray-200
                     shadow-lg shadow-gray-200/50
                     focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500
                     transition-all duration-200
                     placeholder:text-gray-400
                     chatbot-input"
          aria-label="AIHub 챗봇 입력창"
        />
        <button
          type="submit"
          className="absolute right-3 top-1/2 -translate-y-1/2
                     px-5 py-2 rounded-xl
                     bg-gradient-to-r from-indigo-500 to-purple-500
                     text-white text-sm font-medium
                     hover:from-indigo-600 hover:to-purple-600
                     active:scale-95
                     transition-all duration-200
                     shadow-md hover:shadow-lg
                     disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={!input.trim()}
          aria-label="전송"
        >
          전송
        </button>
      </div>
    </form>
  );
}
