import { Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";

const Header = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-6">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg cosmic-gradient flex items-center justify-center">
              <Rocket className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg">NASA BioKnowledge</h1>
              <p className="text-xs text-muted-foreground">Space Biology Engine</p>
            </div>
          </div>
          
          <nav className="hidden md:flex items-center gap-6">
            <a href="#" className="text-sm font-medium hover:text-primary transition-colors">
              Dashboard
            </a>
            <a href="#" className="text-sm font-medium hover:text-primary transition-colors">
              Publications
            </a>
            <a href="#" className="text-sm font-medium hover:text-primary transition-colors">
              Knowledge Graph
            </a>
            <a href="#" className="text-sm font-medium hover:text-primary transition-colors">
              About
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
