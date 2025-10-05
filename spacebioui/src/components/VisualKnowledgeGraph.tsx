import React, { useEffect, useRef, useState } from 'react';
import { Maximize2, Minimize2 } from 'lucide-react';

interface Node {
  id: string;
  label: string;
  type: 'subject' | 'object' | 'predicate';
  x?: number;
  y?: number;
}

interface Edge {
  id: string;
  from: string;
  to: string;
  label: string;
  confidence?: number;
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

interface VisualKnowledgeGraphProps {
  data: GraphData;
  width?: number;
  height?: number;
}

const VisualKnowledgeGraph: React.FC<VisualKnowledgeGraphProps> = ({ 
  data, 
  width = 600, 
  height = 400 
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Dynamic dimensions for fullscreen
  const currentWidth = isFullscreen ? window.innerWidth - 40 : width;
  const currentHeight = isFullscreen ? window.innerHeight - 100 : height;

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = svgRef.current;
    const nodes = [...data.nodes];
    const edges = [...data.edges];

    // Enhanced hierarchical layout with better edge distribution
    const simulation = {
      nodes: nodes.map((node, i) => {
        // Create hierarchical layout: subjects on left, predicates in middle, objects on right
        let x, y;
        const padding = 100;
        const usableWidth = currentWidth - 2 * padding;
        const usableHeight = currentHeight - 2 * padding;
        
        if (node.type === 'subject') {
          x = padding + usableWidth * 0.2;
          y = padding + (usableHeight / Math.max(1, nodes.filter(n => n.type === 'subject').length - 1)) * nodes.filter(n => n.type === 'subject').indexOf(node);
        } else if (node.type === 'object') {
          x = padding + usableWidth * 0.8;
          y = padding + (usableHeight / Math.max(1, nodes.filter(n => n.type === 'object').length - 1)) * nodes.filter(n => n.type === 'object').indexOf(node);
        } else {
          x = padding + usableWidth * 0.5;
          y = padding + (usableHeight / Math.max(1, nodes.filter(n => n.type === 'predicate').length - 1)) * nodes.filter(n => n.type === 'predicate').indexOf(node);
        }
        
        // Add some randomness to avoid perfect alignment
        x += (Math.random() - 0.5) * 60;
        y += (Math.random() - 0.5) * 60;
        
        return {
          ...node,
          x: isNaN(y) ? currentHeight / 2 : x,
          y: isNaN(y) ? currentHeight / 2 : y,
          vx: 0,
          vy: 0
        };
      }),
      tick: function() {
        this.nodes.forEach((node: any, i: number) => {
          // Very strong repulsion between nodes to prevent overlapping
          this.nodes.forEach((other: any, j: number) => {
            if (i !== j) {
              const dx = node.x - other.x;
              const dy = node.y - other.y;
              const distance = Math.sqrt(dx * dx + dy * dy);
              const minDistance = 120; // Minimum distance between nodes
              
              if (distance < minDistance && distance > 0) {
                const force = (minDistance - distance) * 0.8;
                const forceX = (dx / distance) * force;
                const forceY = (dy / distance) * force;
                node.vx += forceX;
                node.vy += forceY;
                other.vx -= forceX;
                other.vy -= forceY;
              }
            }
          });

          // Attraction to ideal positions based on type
          let idealX, idealY;
          const padding = 100;
          const usableWidth = currentWidth - 2 * padding;
          const usableHeight = currentHeight - 2 * padding;
          
          if (node.type === 'subject') {
            idealX = padding + usableWidth * 0.2;
          } else if (node.type === 'object') {
            idealX = padding + usableWidth * 0.8;
          } else {
            idealX = padding + usableWidth * 0.5;
          }
          idealY = currentHeight / 2;
          
          const dx = idealX - node.x;
          const dy = idealY - node.y;
          node.vx += dx * 0.001;
          node.vy += dy * 0.001;

          // Apply velocity with strong damping
          node.vx *= 0.85;
          node.vy *= 0.85;
          node.x += node.vx;
          node.y += node.vy;

          // Keep nodes within bounds with extra padding
          const nodePadding = 80;
          node.x = Math.max(nodePadding, Math.min(currentWidth - nodePadding, node.x));
          node.y = Math.max(nodePadding, Math.min(currentHeight - nodePadding, node.y));
        });
      }
    };

    // Run simulation for longer to achieve better layout
    for (let i = 0; i < 200; i++) {
      simulation.tick();
    }

    // Clear previous content
    svg.innerHTML = '';

    // Create gradients and patterns
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    
    // Arrow marker for edge direction
    const arrowMarker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    arrowMarker.id = 'arrowhead';
    arrowMarker.setAttribute('markerWidth', '10');
    arrowMarker.setAttribute('markerHeight', '7');
    arrowMarker.setAttribute('refX', '9');
    arrowMarker.setAttribute('refY', '3.5');
    arrowMarker.setAttribute('orient', 'auto');
    arrowMarker.innerHTML = `
      <polygon points="0 0, 10 3.5, 0 7" fill="#6b7280" />
    `;
    
    const subjectGradient = document.createElementNS('http://www.w3.org/2000/svg', 'radialGradient');
    subjectGradient.id = 'subjectGradient';
    subjectGradient.innerHTML = `
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="100%" stop-color="#1e40af" />
    `;
    
    const objectGradient = document.createElementNS('http://www.w3.org/2000/svg', 'radialGradient');
    objectGradient.id = 'objectGradient';
    objectGradient.innerHTML = `
      <stop offset="0%" stop-color="#10b981" />
      <stop offset="100%" stop-color="#047857" />
    `;

    const predicateGradient = document.createElementNS('http://www.w3.org/2000/svg', 'radialGradient');
    predicateGradient.id = 'predicateGradient';
    predicateGradient.innerHTML = `
      <stop offset="0%" stop-color="#f59e0b" />
      <stop offset="100%" stop-color="#d97706" />
    `;

    defs.appendChild(arrowMarker);
    defs.appendChild(subjectGradient);
    defs.appendChild(objectGradient);
    defs.appendChild(predicateGradient);
    svg.appendChild(defs);

    // Function to create intelligent curved paths that avoid overlaps
    const createCurvedPath = (fromNode: any, toNode: any, edgeIndex: number, totalEdges: number, allEdges: any[]) => {
      const dx = toNode.x - fromNode.x;
      const dy = toNode.y - fromNode.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      // Calculate node radii
      const fromRadius = fromNode.type === 'predicate' ? 20 : 28;
      const toRadius = toNode.type === 'predicate' ? 20 : 28;
      
      // Adjust start and end points to node edges with arrow clearance
      const arrowClearance = 15; // Extra space for arrow visibility
      const adjustedFromX = fromNode.x + (dx / distance) * (fromRadius + 5);
      const adjustedFromY = fromNode.y + (dy / distance) * (fromRadius + 5);
      const adjustedToX = toNode.x - (dx / distance) * (toRadius + arrowClearance);
      const adjustedToY = toNode.y - (dy / distance) * (toRadius + arrowClearance);
      
      // Calculate optimal curve amount to avoid overlaps
      let curvature = 0;
      const baseOffset = 30; // Base offset for curves
      
      if (totalEdges > 1) {
        // Spread edges evenly around the direct path
        curvature = (edgeIndex - (totalEdges - 1) / 2) * 0.4;
      }
      
      // Check for potential overlaps with other edges and adjust curve
      const tolerance = 50; // Distance tolerance for overlap detection
      allEdges.forEach(otherEdge => {
        if (otherEdge.from !== fromNode.id || otherEdge.to !== toNode.id) {
          const otherFrom = simulation.nodes.find(n => n.id === otherEdge.from);
          const otherTo = simulation.nodes.find(n => n.id === otherEdge.to);
          
          if (otherFrom && otherTo) {
            // Check if paths might intersect
            const midX = (adjustedFromX + adjustedToX) / 2;
            const midY = (adjustedFromY + adjustedToY) / 2;
            const otherMidX = (otherFrom.x + otherTo.x) / 2;
            const otherMidY = (otherFrom.y + otherTo.y) / 2;
            
            const midDistance = Math.sqrt((midX - otherMidX) ** 2 + (midY - otherMidY) ** 2);
            
            if (midDistance < tolerance) {
              // Adjust curvature to avoid overlap
              curvature += Math.sign(curvature || 1) * 0.5;
            }
          }
        }
      });
      
      // Control point for the curve
      const midX = (adjustedFromX + adjustedToX) / 2;
      const midY = (adjustedFromY + adjustedToY) / 2;
      
      // Perpendicular offset for curve with dynamic scaling
      const adjustedDistance = Math.sqrt((adjustedToX - adjustedFromX) ** 2 + (adjustedToY - adjustedFromY) ** 2);
      const perpX = -(adjustedToY - adjustedFromY) / adjustedDistance * curvature * Math.min(adjustedDistance * 0.3, 80);
      const perpY = (adjustedToX - adjustedFromX) / adjustedDistance * curvature * Math.min(adjustedDistance * 0.3, 80);
      
      const controlX = midX + perpX;
      const controlY = midY + perpY;
      
      // Use smooth cubic bezier for better curves
      const control1X = adjustedFromX + (controlX - adjustedFromX) * 0.6;
      const control1Y = adjustedFromY + (controlY - adjustedFromY) * 0.6;
      const control2X = adjustedToX + (controlX - adjustedToX) * 0.6;
      const control2Y = adjustedToY + (controlY - adjustedToY) * 0.6;
      
      return `M ${adjustedFromX} ${adjustedFromY} C ${control1X} ${control1Y}, ${control2X} ${control2Y}, ${adjustedToX} ${adjustedToY}`;
    };

    // Group edges by node pairs to handle multiple edges between same nodes
    const edgeGroups: { [key: string]: any[] } = {};
    edges.forEach((edge, index) => {
      const key = `${edge.from}-${edge.to}`;
      if (!edgeGroups[key]) edgeGroups[key] = [];
      edgeGroups[key].push({ ...edge, index });
    });

    // Draw curved edges with improved routing
    Object.values(edgeGroups).forEach((edgeGroup) => {
      edgeGroup.forEach((edge, groupIndex) => {
        const fromNode = simulation.nodes.find(n => n.id === edge.from);
        const toNode = simulation.nodes.find(n => n.id === edge.to);
        
        if (fromNode && toNode) {
          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          path.setAttribute('d', createCurvedPath(fromNode, toNode, groupIndex, edgeGroup.length, edges));
          path.setAttribute('stroke', '#6b7280');
          path.setAttribute('stroke-width', '2.5');
          path.setAttribute('fill', 'none');
          path.setAttribute('opacity', '0.8');
          path.setAttribute('stroke-linecap', 'round');
          path.setAttribute('marker-end', 'url(#arrowhead)');
          svg.appendChild(path);
        }
      });
    });

    // Draw nodes with better sizing and positioning
    simulation.nodes.forEach(node => {
      const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      group.style.cursor = 'pointer';
      
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', node.x.toString());
      circle.setAttribute('cy', node.y.toString());
      
      // Dynamic sizing based on node type
      const radius = node.type === 'predicate' ? '20' : '28';
      circle.setAttribute('r', radius);
      
      const fillColor = node.type === 'subject' ? 'url(#subjectGradient)' :
                       node.type === 'object' ? 'url(#objectGradient)' :
                       'url(#predicateGradient)';
      circle.setAttribute('fill', fillColor);
      circle.setAttribute('stroke', '#ffffff');
      circle.setAttribute('stroke-width', '3');
      circle.setAttribute('filter', 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))');
      
      if (selectedNode === node.id) {
        circle.setAttribute('stroke', '#fbbf24');
        circle.setAttribute('stroke-width', '4');
      }

      // Add text background for better readability - increased character limit
      const displayLabel = node.label.length > 25 ? node.label.substring(0, 25) + '...' : node.label;
      const textWidth = displayLabel.length * 7;
      
      const textBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      textBg.setAttribute('x', (node.x - textWidth / 2 - 4).toString());
      textBg.setAttribute('y', (node.y + 40).toString());
      textBg.setAttribute('width', (textWidth + 8).toString());
      textBg.setAttribute('height', '18');
      textBg.setAttribute('fill', 'rgba(255, 255, 255, 0.95)');
      textBg.setAttribute('stroke', 'rgba(31, 41, 55, 0.1)');
      textBg.setAttribute('stroke-width', '0.5');
      textBg.setAttribute('rx', '4');

      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', node.x.toString());
      text.setAttribute('y', (node.y + 52).toString());
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('font-size', '12');
      text.setAttribute('font-weight', 'bold');
      text.setAttribute('fill', '#1f2937');
      text.setAttribute('font-family', 'Arial, sans-serif');
      text.textContent = displayLabel;

      group.appendChild(textBg);
      group.appendChild(circle);
      group.appendChild(text);
      
      group.addEventListener('click', () => {
        setSelectedNode(selectedNode === node.id ? null : node.id);
      });
      
      svg.appendChild(group);
    });

  }, [data, currentWidth, currentHeight, selectedNode]);

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

  if (!data.nodes.length) {
    return (
      <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4' : 'space-y-4'}`}>
        {isFullscreen && (
          <div 
            className="fixed inset-0 bg-black/50" 
            onClick={() => setIsFullscreen(false)}
            style={{ zIndex: -1 }}
          />
        )}
        
        <div className={`${isFullscreen ? 'bg-white rounded-lg shadow-2xl p-6' : ''} space-y-4`}>
          <div className="flex justify-between items-center">
            <h4 className="text-sm font-semibold text-gray-700">Graph Visualization</h4>
            <button
              onClick={toggleFullscreen}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md z-10"
              title={isFullscreen ? "Exit Fullscreen (Press Esc)" : "Enter Fullscreen"}
            >
              {isFullscreen ? <Minimize2 size={20} /> : <Maximize2 size={16} />}
            </button>
          </div>
          
          <div 
            className="flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg bg-gray-50"
            style={{ width: currentWidth, height: currentHeight }}
          >
            <div className="text-center text-gray-500">
              <div className="text-4xl mb-2">🌐</div>
              <p>No graph data to display</p>
              <p className="text-sm">Query the knowledge graph to see visualizations</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const selectedNodeData = selectedNode ? data.nodes.find(n => n.id === selectedNode) : null;

  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4' : 'space-y-4'}`}>
      {isFullscreen && (
        <div 
          className="fixed inset-0 bg-black/50" 
          onClick={() => setIsFullscreen(false)}
          style={{ zIndex: -1 }}
        />
      )}
      
      <div className={`${isFullscreen ? 'bg-white rounded-lg shadow-2xl p-6 max-w-full max-h-full overflow-auto' : ''} space-y-4`}>
        <div className="flex justify-between items-center">
          <h4 className="text-sm font-semibold text-gray-700">Graph Visualization</h4>
          <button
            onClick={toggleFullscreen}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors z-10"
            title={isFullscreen ? "Exit Fullscreen (Press Esc)" : "Enter Fullscreen"}
          >
            {isFullscreen ? <Minimize2 size={20} /> : <Maximize2 size={16} />}
          </button>
        </div>

        <div className="relative">
          <svg
            ref={svgRef}
            width={currentWidth}
            height={currentHeight}
            className="border border-gray-200 rounded-lg bg-white shadow-sm"
            viewBox={`0 0 ${currentWidth} ${currentHeight}`}
          />
          
          {isFullscreen && (
            <div className="absolute top-4 right-4 bg-white/90 p-2 rounded-md shadow-sm">
              <div className="flex gap-4 text-xs">
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                  <span>Subjects</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span>Objects</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <span>Predicates</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {selectedNodeData && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-semibold text-blue-800 mb-1">Selected Node</h4>
            <p className="text-sm text-blue-700">
              <strong>Label:</strong> {selectedNodeData.label}
            </p>
            <p className="text-sm text-blue-700">
              <strong>Type:</strong> {selectedNodeData.type}
            </p>
          </div>
        )}
        
        {!isFullscreen && (
          <div className="flex gap-4 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span>Subjects</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span>Objects</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <span>Predicates</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VisualKnowledgeGraph;