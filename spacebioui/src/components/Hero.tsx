import { Search, Brain, Network } from "lucide-react";
import { Button } from "@/components/ui/button";

const Hero = () => {
  return (
    <section className="relative overflow-hidden py-20 px-6">
      <div className="absolute inset-0 cosmic-gradient opacity-10" />
      
      <div className="container mx-auto relative z-10">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-4">
            <Brain className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-primary">AI-Powered Knowledge Engine</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight">
            NASA Space Biology{" "}
            <span 
              className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
              style={{
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}
            >
              Knowledge Graph
            </span>
          </h1>
          
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Explore decades of bioscience research through an intelligent dashboard. 
            Ask questions, visualize connections, and discover insights from space biology publications.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Button size="lg" className="cosmic-gradient text-white border-0 shadow-lg nebula-glow">
              <Search className="mr-2 h-5 w-5" />
              Start Exploring
            </Button>
            <Button size="lg" variant="outline" className="border-primary/30">
              <Network className="mr-2 h-5 w-5" />
              View Knowledge Graph
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12">
            <div className="p-6 rounded-xl bg-card border border-border hover:border-primary/50 transition-all duration-300">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 mx-auto">
                <Search className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">Semantic Search</h3>
              <p className="text-sm text-muted-foreground">
                Natural language queries powered by advanced embeddings
              </p>
            </div>
            
            <div className="p-6 rounded-xl bg-card border border-border hover:border-secondary/50 transition-all duration-300">
              <div className="w-12 h-12 rounded-lg bg-secondary/10 flex items-center justify-center mb-4 mx-auto">
                <Network className="w-6 h-6 text-secondary" />
              </div>
              <h3 className="font-semibold mb-2">Knowledge Graph</h3>
              <p className="text-sm text-muted-foreground">
                Interactive visualization of research relationships
              </p>
            </div>
            
            <div className="p-6 rounded-xl bg-card border border-border hover:border-accent/50 transition-all duration-300">
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4 mx-auto">
                <Brain className="w-6 h-6 text-accent" />
              </div>
              <h3 className="font-semibold mb-2">AI Assistant</h3>
              <p className="text-sm text-muted-foreground">
                Conversational interface with citation tracking
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
