import { useEffect, useRef } from 'react';
import { AnimatePresence } from 'framer-motion';
import ChatMessage from './ChatMessage';
import ThinkingIndicator from './ThinkingIndicator';
import ChatInput from './ChatInput';
import WelcomeScreen from './WelcomeScreen';

export default function ChatWindow({ messages, loading, onSubmit, onRetry, sessionId }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6">
        {isEmpty ? (
          <WelcomeScreen onPromptSelect={onSubmit} />
        ) : (
          <div className="max-w-4xl mx-auto space-y-6">
            <AnimatePresence>
              {messages.map((msg, i) => (
                <ChatMessage
                  key={msg.id || i}
                  message={msg}
                  onRetry={msg.error ? () => onRetry(msg.originalMessage) : null}
                />
              ))}
              {loading && <ThinkingIndicator key="thinking" />}
            </AnimatePresence>
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-white/5 bg-surface-900/80 backdrop-blur-sm px-4 md:px-8 py-4">
        <div className="max-w-4xl mx-auto">
          <ChatInput
            onSubmit={onSubmit}
            loading={loading}
            disabled={false}
          />
        </div>
      </div>
    </div>
  );
}
