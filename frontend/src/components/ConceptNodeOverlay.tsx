import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getQuestNodes } from '@/lib/api';
import { X, Lock } from 'lucide-react';

interface ConceptNode {
  id: number;
  title: string;
  order: number;
  state: 'completed' | 'pending' | 'locked';
}

interface Props {
  questId: number;
  onClose: () => void;
}

const ConceptNodeOverlay = ({ questId, onClose }: Props) => {
  const [nodes, setNodes] = useState<ConceptNode[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getQuestNodes(questId)
      .then((res) => setNodes(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [questId]);

  const handleNodeClick = (node: ConceptNode) => {
    if (node.state === 'locked') return;
    onClose();
    navigate(`/read/${node.id}`);
  };

  const sortedNodes = [...nodes].sort((a, b) => a.order - b.order);

  return (
    <div className="fixed inset-0 z-40 bg-background/90 backdrop-blur-sm flex items-center justify-center">
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 z-50 text-muted-foreground hover:text-foreground border border-border p-2 hover:border-primary transition-colors"
      >
        <X size={20} />
      </button>

      <div className="relative flex flex-col items-center py-16 max-h-[80vh] overflow-y-auto">
        {loading ? (
          <div className="text-primary font-display text-xl tracking-widest animate-pulse">
            LOADING...
          </div>
        ) : (
          sortedNodes.map((node, index) => (
            <div key={node.id} className="flex flex-col items-center">
              {index > 0 && (
                <div
                  className={`w-0.5 h-12 ${
                    node.state === 'completed' || (sortedNodes[index - 1]?.state === 'completed')
                      ? 'bg-primary/40'
                      : 'bg-border'
                  }`}
                />
              )}

              <button
                onClick={() => handleNodeClick(node)}
                disabled={node.state === 'locked'}
                className="group relative"
              >
                <div
                  className={`w-14 h-14 flex items-center justify-center border-2 transition-all ${
                    node.state === 'completed'
                      ? 'border-primary bg-primary/20 glow-red'
                      : node.state === 'pending'
                      ? 'border-node-current bg-node-current/10 animate-pulse-glow cursor-pointer'
                      : 'border-node-locked bg-node-locked/10 cursor-not-allowed opacity-40'
                  }`}
                  style={{ clipPath: 'polygon(50% 0%, 93% 25%, 93% 75%, 50% 100%, 7% 75%, 7% 25%)' }}
                >
                  {node.state === 'locked' ? (
                    <Lock size={16} className="text-node-locked" />
                  ) : (
                    <span className={`font-display font-bold ${
                      node.state === 'completed' ? 'text-primary' : 'text-node-current'
                    }`}>
                      {node.order}
                    </span>
                  )}
                </div>

                <div className={`absolute left-20 top-1/2 -translate-y-1/2 whitespace-nowrap font-display text-sm tracking-wide ${
                  node.state === 'completed'
                    ? 'text-foreground/70'
                    : node.state === 'pending'
                    ? 'text-node-current font-semibold'
                    : 'text-muted-foreground/40'
                }`}>
                  {node.title}
                  {node.state === 'pending' && (
                    <span className="block text-xs font-mono text-node-current/60 tracking-widest uppercase">
                      PENDING
                    </span>
                  )}
                </div>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ConceptNodeOverlay;
