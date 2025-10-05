import { useEffect, useRef, useState } from 'react';
import 'vis-network/styles/vis-network.css';
// Import Network; DataSet may come from vis-data depending on bundler
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { Network, DataSet } from 'vis-network';

export interface Triple {
  subject: string;
  predicate: string;
  object: string;
  confidence: number;
}

interface Props {
  triples: Triple[];
  height?: string;
}

// Simple color mapping for subjects / objects; could be enhanced with backend node types later
const palette = [
  '#4F46E5', '#0EA5E9', '#059669', '#D97706', '#DB2777', '#7C3AED', '#065F46', '#B45309'
];

export const QueryResultGraph = ({ triples, height = '400px' }: Props) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const networkRef = useRef<Network | null>(null);
  const [initError, setInitError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    if (!triples || triples.length === 0) return;
    if (!Network || !DataSet) {
      setInitError('Graph library failed to load');
      return;
    }

    // Build unique nodes map
    const nodeIndex: Record<string, number> = {};
    const nodesArr: any[] = [];
    let idx = 0;

    const ensureNode = (label: string) => {
      if (nodeIndex[label]) return;
      nodeIndex[label] = ++idx;
      const color = palette[(idx - 1) % palette.length];
      nodesArr.push({ id: nodeIndex[label], label, shape: 'dot', size: 14, color });
    };

    const edgesArr: any[] = [];
    triples.slice(0, 60).forEach(t => {
      ensureNode(t.subject);
      ensureNode(t.object);
      edgesArr.push({
        from: nodeIndex[t.subject],
        to: nodeIndex[t.object],
        label: t.predicate,
        arrows: 'to',
        color: t.confidence >= 0.9 ? '#16A34A' : t.confidence >= 0.7 ? '#EAB308' : '#F97316',
        font: { align: 'horizontal', size: 10 }
      });
    });

    const data = { nodes: new DataSet(nodesArr), edges: new DataSet(edgesArr) };

    const options = {
      interaction: { hover: true, tooltipDelay: 150 },
      physics: {
        enabled: true,
        stabilization: { iterations: 120 },
        barnesHut: { gravitationalConstant: -8000, springLength: 110, springConstant: 0.02 }
      },
      layout: { improvedLayout: true },
      edges: { smooth: true }
    } as any;

    try {
      if (networkRef.current) {
        networkRef.current.setData(data);
      } else {
        networkRef.current = new Network(containerRef.current, data, options);
      }
      setInitError(null);
    } catch (e: any) {
      setInitError(e.message || 'Failed to initialize graph');
    }
  }, [triples]);

  return (
    <div className="w-full border rounded-md" style={{ height }}>
      {initError ? (
        <div className="w-full h-full flex items-center justify-center text-xs text-red-500 p-4">
          {initError}
        </div>
      ) : (
        <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
      )}
    </div>
  );
};

export default QueryResultGraph;
