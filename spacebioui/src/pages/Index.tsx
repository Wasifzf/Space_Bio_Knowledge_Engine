import Header from "@/components/Header";
import Hero from "@/components/Hero";
import SearchFilters from "@/components/SearchFilters";
import KnowledgeGraphView from "@/components/KnowledgeGraphView";
import ChatInterface from "@/components/ChatInterface";
import PublicationCards from "@/components/PublicationCards";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <Hero />
        <SearchFilters />
        <div className="grid lg:grid-cols-2 gap-8">
          <KnowledgeGraphView />
          <ChatInterface />
        </div>
        <PublicationCards />
      </main>
      
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
};

export default Index;
