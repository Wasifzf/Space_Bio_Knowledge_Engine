import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Hero from "./components/Hero";
import SimpleKnowledgeGraph from "./components/SimpleKnowledgeGraph";
import SimpleChatInterface from "./components/SimpleChatInterface";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode; fallback?: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('React Error Boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center p-8">
            <h1 className="text-2xl font-bold text-red-600 mb-4">Something went wrong</h1>
            <p className="text-gray-600 mb-4">There was an error loading this component.</p>
            <button 
              onClick={() => this.setState({ hasError: false })}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Safe Index Component
const SafeIndex = () => {
  try {
    return (
      <div className="min-h-screen bg-background">
        <ErrorBoundary>
          <Header />
        </ErrorBoundary>
        
        <ErrorBoundary fallback={
          <div className="py-20 px-6 text-center">
            <h2 className="text-3xl font-bold mb-4">NASA Space Biology Knowledge Graph</h2>
            <p className="text-gray-600">Hero section failed to load</p>
          </div>
        }>
          <Hero />
        </ErrorBoundary>
        
        <ErrorBoundary>
          <main className="container mx-auto px-4 py-8">
            <div className="grid lg:grid-cols-2 gap-8 mb-8">
              <ErrorBoundary fallback={
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold mb-4 text-red-600">Knowledge Graph</h3>
                  <p className="text-gray-600">Failed to load Knowledge Graph component</p>
                  <button 
                    onClick={() => window.location.reload()} 
                    className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Reload Page
                  </button>
                </div>
              }>
                <SimpleKnowledgeGraph />
              </ErrorBoundary>
              
              <ErrorBoundary fallback={
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold mb-4 text-red-600">Chat Interface</h3>
                  <p className="text-gray-600">Failed to load Chat Interface component</p>
                  <button 
                    onClick={() => window.location.reload()} 
                    className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Reload Page
                  </button>
                </div>
              }>
                <SimpleChatInterface />
              </ErrorBoundary>
            </div>
          </main>
        </ErrorBoundary>
        
        <footer className="border-t border-border py-12 px-6 mt-20">
          <div className="container mx-auto">
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg cosmic-gradient flex items-center justify-center">
                  <span className="text-white font-bold text-sm">N</span>
                </div>
                <span className="font-semibold">NASA BioKnowledge Engine</span>
              </div>
              <p className="text-sm text-muted-foreground max-w-md mx-auto">
                An AI-powered platform for exploring NASA space biology research through 
                knowledge graphs and conversational interfaces.
              </p>
              <p className="text-xs text-muted-foreground">
                MVP Demo • Built for NASA Space Apps Challenge
              </p>
            </div>
          </div>
        </footer>
      </div>
    );
  } catch (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Error Loading Application</h1>
          <p className="text-gray-600 mt-2">Please refresh the page</p>
        </div>
      </div>
    );
  }
};

const App = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<SafeIndex />} />
            <Route path="*" element={
              <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                  <h1 className="text-2xl font-bold mb-4">404 - Page Not Found</h1>
                  <a href="/" className="text-blue-600 hover:underline">
                    Return to Home
                  </a>
                </div>
              </div>
            } />
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
