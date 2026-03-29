import { createContext, useContext, useState, ReactNode, useCallback, useRef } from 'react';
import { getSession, completeSession as completeSessionApi } from '@/lib/api';

interface SessionNode {
  id: number;
  title: string;
  order: number;
}

interface Session {
  focus_node: SessionNode | null;
  reinforcement_nodes: SessionNode[];
}

interface SessionContextType {
  session: Session | null;
  nodeCompleted: boolean;
  setNodeCompleted: (v: boolean) => void;
  fetchSession: () => Promise<void>;
  completeSession: () => Promise<void>;
  resetSession: () => void;
}

const SessionContext = createContext<SessionContextType | null>(null);

export const useSession = () => {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSession must be within SessionProvider');
  return ctx;
};

export const SessionProvider = ({ children }: { children: ReactNode }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [nodeCompleted, setNodeCompleted] = useState(false);
  const hasFetched = useRef(false);
  const isFetching = useRef(false);
  const nodeCompletedRef = useRef(false);

  // Keep ref in sync with state
  const setNodeCompletedSafe = useCallback((v: boolean) => {
    nodeCompletedRef.current = v;
    setNodeCompleted(v);
  }, []);

  const fetchSession = useCallback(async () => {
    // Don't re-fetch if user completed a node but hasn't finished session yet
    if (nodeCompletedRef.current) return;
    // Only fetch once; subsequent updates come from completeSession
    if (hasFetched.current) return;
    // Prevent concurrent fetches (strict mode double-mount)
    if (isFetching.current) return;
    isFetching.current = true;
    try {
      const res = await getSession();
      setSession(res.data);
      hasFetched.current = true;
    } finally {
      isFetching.current = false;
    }
  }, []);

  const completeSession = useCallback(async () => {
    if (!session?.focus_node) return;
    const res = await completeSessionApi(session.focus_node.id);
    setSession(res.data);
    setNodeCompletedSafe(false);
    // Allow fetchSession to work again for new session data
    hasFetched.current = true;
  }, [session, setNodeCompletedSafe]);

  const resetSession = useCallback(() => {
    setSession(null);
    setNodeCompletedSafe(false);
    hasFetched.current = false;
    isFetching.current = false;
  }, [setNodeCompletedSafe]);

  return (
    <SessionContext.Provider value={{ session, nodeCompleted, setNodeCompleted: setNodeCompletedSafe, fetchSession, completeSession, resetSession }}>
      {children}
    </SessionContext.Provider>
  );
};
