import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const SearchFilters = () => {
  return (
    <section className="py-8 px-6 border-b border-border bg-card/50 backdrop-blur-sm">
      <div className="container mx-auto">
        <div className="max-w-5xl mx-auto space-y-4">
          <div className="flex gap-4 flex-col md:flex-row">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                placeholder="Ask a question or search publications..."
                className="pl-10 h-12 border-border focus:border-primary"
              />
            </div>
            <Button className="cosmic-gradient text-white h-12 px-8">
              Search
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Select defaultValue="all-organisms">
              <SelectTrigger className="border-border">
                <SelectValue placeholder="Organism" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-organisms">All Organisms</SelectItem>
                <SelectItem value="arabidopsis">Arabidopsis</SelectItem>
                <SelectItem value="mice">Mice</SelectItem>
                <SelectItem value="c-elegans">C. elegans</SelectItem>
                <SelectItem value="bacteria">Bacteria</SelectItem>
              </SelectContent>
            </Select>
            
            <Select defaultValue="all-conditions">
              <SelectTrigger className="border-border">
                <SelectValue placeholder="Condition" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-conditions">All Conditions</SelectItem>
                <SelectItem value="microgravity">Microgravity</SelectItem>
                <SelectItem value="radiation">Radiation</SelectItem>
                <SelectItem value="hypergravity">Hypergravity</SelectItem>
                <SelectItem value="combined">Combined Factors</SelectItem>
              </SelectContent>
            </Select>
            
            <Select defaultValue="all-missions">
              <SelectTrigger className="border-border">
                <SelectValue placeholder="Mission" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-missions">All Missions</SelectItem>
                <SelectItem value="iss">ISS</SelectItem>
                <SelectItem value="shuttle">Space Shuttle</SelectItem>
                <SelectItem value="biosatellite">Biosatellite</SelectItem>
                <SelectItem value="ground">Ground Control</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SearchFilters;
