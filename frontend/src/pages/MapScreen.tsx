import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getQuests, getQuestNodes } from '@/lib/api';
import { useSession } from '@/contexts/SessionContext';
import { useAuth } from '@/contexts/AuthContext';
import SessionSidebar from '@/components/SessionSidebar';
import ConceptNodeOverlay from '@/components/ConceptNodeOverlay';
import { ChevronRight, BarChart3, LogOut } from 'lucide-react';

interface Quest {
  id: number;
  title: string;
  order: number;
  is_completed: boolean;
}

const MapScreen = () => {
  const [quests, setQuests] = useState<Quest[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [overlayQuestId, setOverlayQuestId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const { fetchSession, resetSession } = useSession();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    resetSession();
    await logout();
  };

  const loadQuests = async () => {
    try {
      const res = await getQuests();
      setQuests(res.data);
    } catch { /* handled by interceptor */ }
  };

  useEffect(() => {
    const init = async () => {
      await Promise.all([loadQuests(), fetchSession()]);
      setLoading(false);
    };
    init();
  }, []);

  // Sort quests by order ascending, display bottom to top
  const sortedQuests = [...quests].sort((a, b) => a.order - b.order);

  const handleQuestClick = (questId: number) => {
    setOverlayQuestId(questId);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-primary font-display text-2xl tracking-widest animate-pulse">
          LOADING...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background grid */}
      <div className="fixed inset-0 opacity-[0.03]" style={{
        backgroundImage: 'linear-gradient(hsl(var(--border)) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--border)) 1px, transparent 1px)',
        backgroundSize: '40px 40px',
      }} />

      {/* Top bar */}
      <div className="fixed top-0 left-0 right-0 z-30 bg-background/80 backdrop-blur border-b border-border">
        <div className="flex items-center justify-between px-6 py-3">
          <h1 className="font-display text-xl font-bold tracking-wider text-primary text-shadow-glow">
            LEVEL UP
          </h1>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 px-3 py-1.5 border border-border text-muted-foreground hover:text-foreground hover:border-primary transition-colors font-mono text-xs tracking-wider uppercase"
            >
              <BarChart3 size={14} />
              STATS
            </button>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-1.5 border border-border text-muted-foreground hover:text-destructive hover:border-destructive transition-colors font-mono text-xs tracking-wider uppercase"
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Quest Map */}
      <div className="relative flex flex-col items-center pt-20 pb-32 min-h-screen justify-end">
        {sortedQuests.map((quest, index) => {
          const isCompleted = quest.is_completed;
          const isCurrent = !isCompleted && (index === sortedQuests.length - 1 || sortedQuests.slice(index + 1).every(q => q.is_completed));
          // Actually: current = last with is_completed: false
          const isCurrentQuest = !quest.is_completed;

          return (
            <div key={quest.id} className="flex flex-col items-center">
              {/* Path line above (except first/bottom) */}
              {index > 0 && (
                <div
                  className={`w-0.5 h-16 transition-colors ${
                    isCompleted ? 'bg-primary/60' : 'bg-border'
                  }`}
                />
              )}

              {/* Quest Node */}
              <button
                onClick={() => handleQuestClick(quest.id)}
                className="group relative"
              >
                {/* Node circle */}
                <div
                  className={`w-16 h-16 flex items-center justify-center border-2 transition-all ${
                    isCompleted
                      ? 'border-primary bg-primary/20 glow-red'
                      : 'border-node-current bg-node-current/10 animate-pulse-glow'
                  }`}
                  style={{ clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)' }}
                >
                  <span className={`font-display font-bold text-lg ${
                    isCompleted ? 'text-primary' : 'text-node-current'
                  }`}>
                    {quest.order}
                  </span>
                </div>

                {/* Label */}
                <div className={`absolute left-20 top-1/2 -translate-y-1/2 whitespace-nowrap font-display text-sm tracking-wide transition-colors ${
                  isCompleted
                    ? 'text-foreground/70'
                    : 'text-node-current font-semibold'
                }`}>
                  {quest.title}
                  {isCurrentQuest && (
                    <span className="block text-xs font-mono text-node-current/60 tracking-widest uppercase">
                      CURRENT
                    </span>
                  )}
                </div>
              </button>
            </div>
          );
        })}
      </div>

      {/* Session Toggle Button */}
      <button
        onClick={() => setSidebarOpen(true)}
        className="fixed right-0 top-1/2 -translate-y-1/2 z-20 bg-primary/90 text-primary-foreground px-2 py-8 font-display font-bold text-xs tracking-widest uppercase hover:bg-primary transition-colors"
        style={{ writingMode: 'vertical-rl' }}
      >
        <ChevronRight size={14} className="mb-2 rotate-180" />
        SESSION
      </button>

      {/* Session Sidebar */}
      <SessionSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} onQuestsRefresh={loadQuests} />

      {/* ConceptNode Overlay */}
      {overlayQuestId !== null && (
        <ConceptNodeOverlay
          questId={overlayQuestId}
          onClose={() => setOverlayQuestId(null)}
        />
      )}
    </div>
  );
};

export default MapScreen;
