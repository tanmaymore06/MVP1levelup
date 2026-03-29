import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDashboard } from '@/lib/api';
import { ArrowLeft, Flame, Shield, BookCheck, Zap } from 'lucide-react';

interface DashboardData {
  streak: number;
  freeze_streak: number;
  total_nodes_completed: number;
  total_sessions_completed: number;
  current_quest_title: string | null;
  current_quest_progress: { completed: number; total: number } | null;
}

const Dashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getDashboard()
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-primary font-display text-2xl tracking-widest animate-pulse">
          LOADING...
        </div>
      </div>
    );
  }

  if (!data) return null;

  const stats = [
    { icon: Flame, label: 'STREAK', value: `${data.streak} days`, color: 'text-node-current' },
    { icon: Shield, label: 'FREEZE TOKENS', value: `${data.freeze_streak}`, color: 'text-primary' },
    { icon: BookCheck, label: 'NODES COMPLETED', value: `${data.total_nodes_completed}`, color: 'text-primary' },
    { icon: Zap, label: 'SESSIONS DONE', value: `${data.total_sessions_completed}`, color: 'text-node-current' },
  ];

  const progress = data.current_quest_progress;
  const progressPct = progress ? (progress.completed / progress.total) * 100 : 0;

  return (
    <div className="min-h-screen bg-background">
      {/* Background */}
      <div className="fixed inset-0 opacity-[0.03]" style={{
        backgroundImage: 'linear-gradient(hsl(var(--border)) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--border)) 1px, transparent 1px)',
        backgroundSize: '40px 40px',
      }} />

      {/* Top bar */}
      <div className="relative z-10 border-b border-border bg-background/80 backdrop-blur">
        <div className="max-w-3xl mx-auto flex items-center justify-between px-6 py-3">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors font-mono text-xs tracking-wider uppercase"
          >
            <ArrowLeft size={14} />
            BACK TO MAP
          </button>
          <h1 className="font-display text-lg font-bold tracking-wider text-primary uppercase">
            DASHBOARD
          </h1>
          <div className="w-24" />
        </div>
      </div>

      <div className="relative z-10 max-w-3xl mx-auto px-6 py-10 space-y-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          {stats.map((stat) => (
            <div key={stat.label} className="bg-card border border-border p-5 relative">
              <div className="absolute top-0 left-0 w-8 h-0.5 bg-primary" />
              <div className="flex items-center gap-3 mb-2">
                <stat.icon size={18} className={stat.color} />
                <span className="font-mono text-[10px] tracking-widest uppercase text-muted-foreground">
                  {stat.label}
                </span>
              </div>
              <span className="font-display text-3xl font-bold text-foreground">
                {stat.value}
              </span>
            </div>
          ))}
        </div>

        {/* Current Quest */}
        <div className="bg-card border border-border p-6 relative">
          <div className="absolute top-0 left-0 w-12 h-0.5 bg-primary" />
          <span className="font-mono text-[10px] tracking-widest uppercase text-muted-foreground">
            Current Quest
          </span>

          {data.current_quest_title ? (
            <>
              <h2 className="font-display text-xl font-bold text-foreground mt-2">
                {data.current_quest_title}
              </h2>
              {progress && (
                <div className="mt-4">
                  <div className="flex justify-between mb-2">
                    <span className="font-mono text-xs text-muted-foreground">Progress</span>
                    <span className="font-mono text-xs text-primary">
                      {progress.completed}/{progress.total}
                    </span>
                  </div>
                  <div className="w-full h-2 bg-background border border-border">
                    <div
                      className="h-full bg-primary transition-all duration-500"
                      style={{ width: `${progressPct}%` }}
                    />
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="font-display text-foreground/70 mt-2">
              You have completed all available content.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
