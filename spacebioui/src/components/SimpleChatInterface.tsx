import { useState, useEffect } from "react";
import { Maximize2, Minimize2, RotateCcw, Info } from "lucide-react";
import MarkdownRenderer from "./MarkdownRenderer";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  metadata?: {
    vector_results?: number;
    kg_relationships?: number;
  };
}

const SimpleChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your AI assistant for NASA space biology research. Ask me anything about bioscience publications, organisms in space, or specific research findings!"
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [memoryStatus, setMemoryStatus] = useState<{
    conversation_length: number;
    memory_enabled: boolean;
  } | null>(null);

  const clearMemory = async () => {
    try {
      const response = await fetch('http://localhost:8000/chat/clear-memory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        setMessages([{
          id: "1",
          role: "assistant",
          content: "Memory cleared! I'm starting fresh. How can I help you with space biology research?"
        }]);
        fetchMemoryStatus();
      }
    } catch (error) {
      console.error('Error clearing memory:', error);
    }
  };

  const fetchMemoryStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/chat/memory-status');
      if (response.ok) {
        const status = await response.json();
        setMemoryStatus(status);
      }
    } catch (error) {
      console.error('Error fetching memory status:', error);
    }
  };

  // Fetch memory status on component mount
  useEffect(() => {
    fetchMemoryStatus();
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: currentInput, 
          top_k: 3, 
          include_kg: true 
        })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer || "I couldn't process that request.",
        metadata: {
          vector_results: data.vector_results,
          kg_relationships: data.kg_relationships
        }
      };
      
      setMessages(prev => [...prev, aiMessage]);
      fetchMemoryStatus(); // Update memory status after new message
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : "Unknown error"}. Make sure the backend is running on port 8000.`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  // Handle escape key to exit fullscreen
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isFullscreen]);

  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4' : ''}`}>
      {isFullscreen && (
        <div 
          className="fixed inset-0 bg-black/50" 
          onClick={() => setIsFullscreen(false)}
          style={{ zIndex: -1 }}
        />
      )}
      
      <div className={`${isFullscreen ? 'bg-white rounded-lg shadow-2xl h-full w-full max-w-6xl max-h-full overflow-hidden' : 'bg-white border border-gray-200 h-full'} p-6 rounded-lg flex flex-col`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-green-600 rounded flex items-center justify-center">
              <span className="text-white text-sm">🤖</span>
            </div>
            <div>
              <h3 className="text-xl font-semibold">AI Chat Assistant</h3>
              {memoryStatus && (
                <p className="text-xs text-gray-500">
                  💾 {memoryStatus.conversation_length} exchanges remembered
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={clearMemory}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
              title="Clear conversation memory"
            >
              <RotateCcw size={16} />
            </button>
            <button
              onClick={toggleFullscreen}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors z-10"
              title={isFullscreen ? "Exit Fullscreen (Press Esc)" : "Enter Fullscreen"}
            >
              {isFullscreen ? <Minimize2 size={20} /> : <Maximize2 size={16} />}
            </button>
          </div>
        </div>
        
        <div className={`flex-1 overflow-y-auto space-y-4 mb-4 ${isFullscreen ? 'max-h-full' : 'max-h-96'}`}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`${isFullscreen ? 'max-w-4xl' : 'max-w-full lg:max-w-4xl'} px-4 py-3 rounded-lg ${
                  message.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-50 text-gray-800 border border-gray-200"
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  {message.role === "user" ? (
                    <span className="text-xs font-medium">👤 You</span>
                  ) : (
                    <span className="text-xs font-medium">🤖 NASA Space Biology AI</span>
                  )}
                  {message.metadata && (
                    <span className="text-xs opacity-75 bg-white/20 px-2 py-1 rounded">
                      📊 {message.metadata.vector_results} papers • 🧠 {message.metadata.kg_relationships} relationships
                    </span>
                  )}
                </div>
                {message.role === "assistant" ? (
                  <MarkdownRenderer content={message.content} className="text-sm" />
                ) : (
                  <p className="text-sm">{message.content}</p>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-800 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                <div className="flex items-center gap-2">
                  <span className="text-xs">🤖 AI</span>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about space biology research..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "..." : "Send"}
          </button>
        </div>
        
        <div className="text-xs text-gray-500 mt-2">
          Backend: http://localhost:8000 • Vector + Knowledge Graph powered
        </div>
      </div>
    </div>
  );
};

export default SimpleChatInterface;