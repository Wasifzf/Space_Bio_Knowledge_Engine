import { ExternalLink, Calendar, Beaker } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const mockPublications = [
  {
    id: "GLDS-123",
    title: "Gene Expression Changes in Arabidopsis Under Microgravity Conditions",
    organism: "Arabidopsis",
    condition: "Microgravity",
    mission: "ISS",
    date: "2023-06",
    abstract: "This study investigated gene expression patterns in Arabidopsis plants exposed to microgravity conditions aboard the International Space Station...",
  },
  {
    id: "GLDS-245",
    title: "Root Orientation and Growth Pathway Alterations in Space-Grown Plants",
    organism: "Arabidopsis",
    condition: "Microgravity",
    mission: "ISS",
    date: "2023-09",
    abstract: "Analysis of root development and orientation mechanisms in microgravity revealed significant alterations in gravitropism and growth pathways...",
  },
  {
    id: "LSDA-456",
    title: "Muscle Atrophy Mechanisms in Mice During Extended Spaceflight",
    organism: "Mice",
    condition: "Microgravity",
    mission: "Space Shuttle",
    date: "2022-11",
    abstract: "Investigation of cellular mechanisms underlying muscle loss in mice during long-duration spaceflight missions...",
  },
];

const PublicationCards = () => {
  return (
    <section className="py-8 px-6 bg-muted/30">
      <div className="container mx-auto">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <h2 className="text-2xl font-bold mb-2">Recent Publications</h2>
            <p className="text-muted-foreground">
              Curated bioscience research from NASA missions
            </p>
          </div>
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {mockPublications.map((pub) => (
              <Card
                key={pub.id}
                className="p-6 border-border bg-card hover:border-primary/50 transition-all duration-300 flex flex-col"
              >
                <div className="flex items-start justify-between mb-3">
                  <Badge variant="outline" className="border-primary/30 text-primary">
                    {pub.id}
                  </Badge>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                </div>
                
                <h3 className="font-semibold mb-3 line-clamp-2">
                  {pub.title}
                </h3>
                
                <p className="text-sm text-muted-foreground mb-4 line-clamp-3 flex-grow">
                  {pub.abstract}
                </p>
                
                <div className="space-y-2 pt-4 border-t border-border">
                  <div className="flex items-center gap-2 text-sm">
                    <Beaker className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">{pub.organism}</span>
                    <Badge variant="secondary" className="ml-auto">
                      {pub.condition}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="h-4 w-4" />
                    <span>{pub.mission}</span>
                    <span className="ml-auto">{pub.date}</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default PublicationCards;
