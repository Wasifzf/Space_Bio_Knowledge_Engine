import { useState } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { apiClient, EnhancedChatResponse } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: string[];
  metadata?: {
    vector_results?: number;
    kg_relationships?: number;
  };
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your AI assistant for NASA space biology research. Ask me anything about bioscience publications, organisms in space, or specific research findings. I can query our knowledge graph of 776 research relationships from 160 papers!",
      citations: []
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

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
      const response: EnhancedChatResponse = await apiClient.sendChatMessage(currentInput, { top_k: 3, include_kg: true });
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        metadata: {
          vector_results: response.vector_results,
          kg_relationships: response.kg_relationships
        }
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error while processing your request. Please make sure the backend server is running at localhost:8000.",
      };
      setMessages(prev => [...prev, errorMessage]);
      toast({
        title: 'Chat Error',
        description: 'Failed to reach backend /chat endpoint.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="py-8 px-6">
      <div className="container mx-auto">
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <h2 className="text-2xl font-bold mb-2">AI Research Assistant</h2>
            <p className="text-muted-foreground">
              Ask questions about space biology research
            </p>
          </div>
          
          <Card className="border-border bg-card">
            <ScrollArea className="h-[400px] p-6">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {message.role === "assistant" && (
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <Bot className="w-5 h-5 text-primary" />
                      </div>
                    )}
                    
                    <div
                      className={`rounded-lg p-4 max-w-[80%] ${
                        message.role === "user"
                          ? "cosmic-gradient text-white"
                          : "bg-muted"
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      
                      {message.metadata && message.role === "assistant" && (
                        <div className="mt-3 pt-3 border-t border-border/50">
                          <p className="text-xs font-semibold mb-2">Query Results:</p>
                          <div className="flex flex-wrap gap-2">
                            <span className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                              📄 {message.metadata.vector_results} vector docs
                            </span>
                            <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                              🔗 {message.metadata.kg_relationships} relationships
                            </span>
                          </div>
                        </div>
                      )}
                      
                      {message.citations && message.citations.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-border/50">
                          <p className="text-xs font-semibold mb-2">Sources:</p>
                          <div className="flex flex-wrap gap-2">
                            {message.citations.map((citation, idx) => (
                              <span
                                key={idx}
                                className="text-xs px-2 py-1 rounded bg-primary/10 text-primary"
                              >
                                {citation}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {message.role === "user" && (
                      <div className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
                        <User className="w-5 h-5 text-accent" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </ScrollArea>
            
            <div className="p-4 border-t border-border">
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && !isLoading && handleSend()}
                  placeholder="Ask about space biology research..."
                  className="border-border"
                  disabled={isLoading}
                />
                <Button 
                  onClick={handleSend}
                  className="cosmic-gradient text-white"
                  disabled={isLoading || !input.trim()}
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {isLoading && (
                <p className="text-xs text-muted-foreground mt-2">
                  🔍 Searching knowledge graph and documents...
                </p>
              )}
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default ChatInterface;
