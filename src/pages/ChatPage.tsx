import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { gsap } from 'gsap';
import { ArrowLeft, Check, Copy, Send, Sparkles } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatResponse {
  message: string;
  session_id: string;
  stage: string;
  suggestions: string[];
}

const ChatPage = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [currentStage, setCurrentStage] = useState<string>('greeting');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const pageRef = useRef<HTMLDivElement>(null);

  // Particle animation state
  const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number; size: number; speed: number; opacity: number }>>([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (inputRef.current && messages.length === 0) {
      inputRef.current.focus();
    }
  }, [messages.length]);

  // Page entrance animation - simplified to prevent white screen
  useEffect(() => {
    if (pageRef.current) {
      // Simple fade in without blur to prevent white screen
      gsap.fromTo(pageRef.current, {
        opacity: 0,
        y: 20
      }, {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: "power2.out"
      });
    }
  }, []);

  // Initialize particles
  useEffect(() => {
    const newParticles = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 3 + 1,
      speed: Math.random() * 0.5 + 0.1,
      opacity: Math.random() * 0.5 + 0.3
    }));
    setParticles(newParticles);

    // Animate particles
    const interval = setInterval(() => {
      setParticles(prev => prev.map(particle => ({
        ...particle,
        y: particle.y - particle.speed,
        opacity: particle.opacity + (Math.random() - 0.5) * 0.1
      })));
    }, 50);

    return () => clearInterval(interval);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('https://astrologer-9gwv.onrender.com/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [
            ...messages.map(msg => ({
              role: msg.role,
              content: msg.content
            })),
            {
              role: 'user',
              content: inputMessage.trim()
            }
          ],
          session_id: sessionId
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data: ChatResponse = await response.json();
      
      setSessionId(data.session_id);
      setCurrentStage(data.stage);
      setSuggestions(data.suggestions);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I\'m having trouble connecting right now. Please try again in a moment.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const copyToClipboard = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const getQuickQuestions = () => {
    if (suggestions && suggestions.length > 0) {
      return suggestions;
    }
    // Return different questions based on current stage
    if (currentStage === 'greeting') {
      return [
        "I'm having career-related issues",
        "I'm facing problems in my relationships",
        "I'm experiencing financial difficulties",
        "I have health concerns"
      ];
    } else if (currentStage === 'understanding') {
      return [
        "This has been affecting me for months",
        "It's impacting my daily life",
        "I've tried everything but nothing works",
        "I feel stuck and need guidance"
      ];
    } else {
      return [
        "What planetary influences are causing this?",
        "What specific remedies do you recommend?",
        "Are there any mantras I should chant?",
        "What gemstones would be beneficial?"
      ];
    }
  };

  const handleBackClick = () => {
    // Simple back navigation without page fade
    window.history.back();
  };

  // If no messages yet, show the initial input interface
  if (messages.length === 0) {
    return (
      <div ref={pageRef} className="page-transition-container min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 relative overflow-hidden">
        {/* Particle Animation Background */}
        <div className="absolute inset-0">
          {particles.map(particle => (
            <div
              key={particle.id}
              className="absolute bg-blue-300/30 rounded-full animate-pulse"
              style={{
                left: `${particle.x}%`,
                top: `${particle.y}%`,
                width: `${particle.size}px`,
                height: `${particle.size}px`,
                opacity: particle.opacity,
                animationDuration: `${2 + Math.random() * 3}s`,
                animationDelay: `${Math.random() * 2}s`
              }}
            />
          ))}
        </div>

        {/* Header */}
        <div className="relative z-10 p-4">
          <Button 
            onClick={handleBackClick}
            variant="ghost" 
            size="sm" 
            className="text-blue-200 hover:text-white hover:bg-blue-800/30"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
        </div>

        {/* Main Content */}
        <div className="relative z-10 min-h-screen flex items-center justify-center px-6">
          <div className="text-center max-w-2xl mx-auto">
            {/* Welcome Message */}
            <div className="mb-8">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <Sparkles className="w-8 h-8 text-blue-300 animate-pulse" />
                <h1 className="text-4xl font-bold text-white">Pandit Pradeep Kiradoo</h1>
                <Sparkles className="w-8 h-8 text-blue-300 animate-pulse" />
              </div>
              <p className="text-lg text-blue-200 mb-2">Vedic Astrology Consultation</p>
              <p className="text-sm text-blue-300">Ask me anything about your birth chart, planetary influences, or life guidance</p>
            </div>

            {/* Input Box */}
            <Card className="bg-white/10 backdrop-blur-xl border border-white/20 p-6 shadow-2xl">
              <div className="flex space-x-3">
                <Input
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask Pandit Ji anything..."
                  className="flex-1 bg-white/20 border-white/30 text-white placeholder-white/60 focus:border-blue-400 focus:bg-white/30"
                  disabled={isLoading}
                />
                <Button
                  onClick={sendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </Card>

            {/* Quick Questions */}
            <div className="mt-6">
              <p className="text-sm text-blue-300 mb-3">Try asking:</p>
              <div className="flex flex-wrap justify-center gap-2">
                {getQuickQuestions().map((question, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setInputMessage(question);
                      setTimeout(() => sendMessage(), 100);
                    }}
                    className="text-xs bg-white/10 hover:bg-white/20 text-white px-3 py-2 rounded-full border border-white/20 transition-all hover:scale-105"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Chat interface after first message
  return (
    <div ref={pageRef} className="page-transition-container min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 relative overflow-hidden">
      {/* Particle Animation Background */}
      <div className="absolute inset-0">
        {particles.map(particle => (
          <div
            key={particle.id}
            className="absolute bg-blue-300/20 rounded-full animate-pulse"
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`,
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              opacity: particle.opacity,
              animationDuration: `${2 + Math.random() * 3}s`,
              animationDelay: `${Math.random() * 2}s`
            }}
          />
        ))}
      </div>

      {/* Header */}
      <div className="relative z-10 bg-white/10 backdrop-blur-xl border-b border-white/20 p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button 
              onClick={handleBackClick}
              variant="ghost" 
              size="sm" 
              className="text-blue-200 hover:text-white hover:bg-blue-800/30"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-blue-300" />
              <h1 className="text-lg font-semibold text-white">Pandit Pradeep Kiradoo</h1>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-green-400">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm">Online</span>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="relative z-10 max-w-4xl mx-auto p-4">
        <div className="space-y-4 mb-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <Card className={`max-w-[80%] p-4 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white/10 backdrop-blur-xl border border-white/20 text-white'
              }`}>
                <div className="text-sm leading-relaxed">
                  {message.role === 'assistant' ? (
                    <div className="prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown 
                        components={{
                          h1: ({children}) => <h1 className="text-lg font-bold text-blue-300 mb-2">{children}</h1>,
                          h2: ({children}) => <h2 className="text-base font-bold text-blue-300 mb-2">{children}</h2>,
                          h3: ({children}) => <h3 className="text-sm font-bold text-blue-300 mb-1">{children}</h3>,
                          p: ({children}) => <p className="mb-2 text-white">{children}</p>,
                          ul: ({children}) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                          ol: ({children}) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                          li: ({children}) => <li className="text-white">{children}</li>,
                          strong: ({children}) => <strong className="font-bold text-blue-300">{children}</strong>,
                          em: ({children}) => <em className="italic text-blue-200">{children}</em>,
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-white">{message.content}</p>
                  )}
                </div>
                <div className="flex items-center justify-between mt-2">
                  <p className="text-xs opacity-60">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                  {message.role === 'assistant' && currentStage === 'analysis' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(message.content, message.id)}
                      className="text-blue-300 hover:text-white hover:bg-blue-800/30 p-1 h-6"
                    >
                      {copiedMessageId === message.id ? (
                        <Check className="w-3 h-3" />
                      ) : (
                        <Copy className="w-3 h-3" />
                      )}
                    </Button>
                  )}
                </div>
              </Card>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <Card className="bg-white/10 backdrop-blur-xl border border-white/20 p-4 max-w-[80%]">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-300 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-blue-300 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-blue-300 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-white">Pandit Ji is typing...</span>
                </div>
              </Card>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <Card className="bg-white/10 backdrop-blur-xl border border-white/20 p-4">
          <div className="flex space-x-3">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask Pandit Ji anything..."
              className="flex-1 bg-white/20 border-white/30 text-white placeholder-white/60 focus:border-blue-400 focus:bg-white/30"
              disabled={isLoading}
            />
            <Button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ChatPage;
