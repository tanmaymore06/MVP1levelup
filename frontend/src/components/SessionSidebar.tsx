import { useNavigate } from 'react-router-dom';
import { useSession } from '@/contexts/SessionContext';
import { getQuests } from '@/lib/api';
import { X, Target, RotateCcw } from 'lucide-react';

interface Props {
  open: boolean;
  onClose: () => void;
  onQuestsRefresh: () => Promise<void>;
}

const SessionSidebar = ({ open, onClose, onQuestsRefresh }: Props) => {
  const { session, nodeCompleted, completeSession } = useSession();
  const navigate = useNavigate();

  const handleFinishSession = async () => {
    await completeSession();
    await onQuestsRefresh();
  };

  const handleNodeClick = (nodeId: number) => {
    onClose();
    navigate(`/read/${nodeId}`);
  };

  return (
    <>
      {/* Backdrop */}
      {open && (
        <div className="fixed inset-0 z-40 bg-background/40" onClick={onClose} />
      )}

      {/* Sidebar */}
      <div
        className={`fixed top-0 right-0 h-full z-50 w-[380px] max-w-[90vw] bg-card border-l border-border transform transition-transform duration-300 ${
          open ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="font-display text-lg font-bold tracking-wider uppercase text-foreground">
            Session
          </h2>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="p-4 space-y-6 overflow-y-auto h-[calc(100%-130px)]">
          {/* Focus Node */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Target size={14} className="text-node-current" />
              <span className="font-mono text-xs tracking-widest uppercase text-node-current">
                Focus Node
              </span>
            </div>

            {session?.focus_node ? (
              <button
                onClick={() => handleNodeClick(session.focus_node!.id)}
                className="w-full text-left bg-background border border-node-current/30 p-4 hover:border-node-current transition-colors group"
              >
                <span className="font-display text-base font-semibold text-foreground group-hover:text-node-current transition-colors">
                  {session.focus_node.title}
                </span>
                <span className="block text-xs font-mono text-node-current/60 mt-1 tracking-widest uppercase">
                  Your current focus
                </span>
              </button>
            ) : (
              <div className="bg-background border border-border p-4 text-muted-foreground text-sm font-mono">
                You have completed all available content.
              </div>
            )}
          </div>

          {/* Reinforcement Nodes */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <RotateCcw size={14} className="text-primary" />
              <span className="font-mono text-xs tracking-widest uppercase text-primary">
                Reinforcement
              </span>
            </div>

            {session?.reinforcement_nodes && session.reinforcement_nodes.length > 0 ? (
              <div className="space-y-2">
                {session.reinforcement_nodes.map((node) => (
                  <button
                    key={node.id}
                    onClick={() => handleNodeClick(node.id)}
                    className="w-full text-left bg-background border border-border p-3 hover:border-primary/50 transition-colors group"
                  >
                    <span className="font-display text-sm text-foreground/80 group-hover:text-foreground transition-colors">
                      {node.title}
                    </span>
                    <span className="block text-xs font-mono text-muted-foreground mt-0.5 tracking-widest uppercase">
                      Revisit
                    </span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="bg-background border border-border p-3 text-muted-foreground text-sm font-mono">
                Complete more concepts to unlock reinforcement.
              </div>
            )}
          </div>
        </div>

        {/* Finish Session Button */}
        {session?.focus_node && (
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border bg-card">
            <button
              onClick={handleFinishSession}
              disabled={!nodeCompleted}
              className={`w-full py-3 font-display font-bold text-lg tracking-wider uppercase transition-all clip-sharp ${
                nodeCompleted
                  ? 'bg-primary text-primary-foreground hover:brightness-110'
                  : 'bg-muted text-muted-foreground cursor-not-allowed'
              }`}
            >
              FINISH SESSION
            </button>
          </div>
        )}
      </div>
    </>
  );
};

export default SessionSidebar;
