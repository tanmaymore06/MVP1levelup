import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getNodePages, completePage } from '@/lib/api';
import { useSession } from '@/contexts/SessionContext';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import { ArrowLeft, ChevronLeft, ChevronRight } from 'lucide-react';

interface Page {
  id: number;
  title: string;
  content: string;
  order: number;
}

const ReadingScreen = () => {
  const { node_id } = useParams<{ node_id: string }>();
  const [pages, setPages] = useState<Page[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const { setNodeCompleted } = useSession();
  const navigate = useNavigate();

  useEffect(() => {
    if (!node_id) return;
    getNodePages(parseInt(node_id))
      .then((res) => {
        const sorted = [...res.data].sort((a: Page, b: Page) => a.order - b.order);
        setPages(sorted);
        setCurrentIndex(0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [node_id]);

  const currentPage = pages[currentIndex];
  const isLastPage = currentIndex === pages.length - 1;
  const isFirstPage = currentIndex === 0;

  const handleComplete = async (pageId: number) => {
    setCompleting(true);
    try {
      const res = await completePage(pageId);
      if (res.data.node_completed) {
        setNodeCompleted(true);
      }
    } catch { /* ignore */ }
    setCompleting(false);
  };

  const handleNext = async () => {
    if (!currentPage) return;
    await handleComplete(currentPage.id);
    setCurrentIndex((i) => i + 1);
  };

  const handleFinish = async () => {
    if (!currentPage) return;
    await handleComplete(currentPage.id);
    navigate('/');
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

  if (!currentPage) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-muted-foreground font-mono">No pages found.</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Top bar */}
      <div className="fixed top-0 left-0 right-0 z-30 bg-background/80 backdrop-blur border-b border-border">
        <div className="flex items-center justify-between px-6 py-3 max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors font-mono text-xs tracking-wider uppercase"
          >
            <ArrowLeft size={14} />
            BACK TO MAP
          </button>
          <span className="font-mono text-xs text-muted-foreground tracking-widest">
            PAGE {currentIndex + 1} OF {pages.length}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-[800px] mx-auto px-6 pt-20 pb-32">
        {currentPage.title && (
          <h1 className="font-display text-3xl font-bold text-foreground mb-6 tracking-wide border-b border-border pb-4">
            {currentPage.title}
          </h1>
        )}

        <div className="markdown-content text-foreground/85 leading-relaxed text-base">
          <ReactMarkdown
            remarkPlugins={[remarkMath]}
            rehypePlugins={[rehypeKatex, rehypeRaw]}
          >
            {currentPage.content}
          </ReactMarkdown>
        </div>
      </div>

      {/* Bottom navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-background/90 backdrop-blur border-t border-border">
        <div className="max-w-[800px] mx-auto px-6 py-4 flex items-center justify-between">
          <button
            onClick={() => setCurrentIndex((i) => i - 1)}
            disabled={isFirstPage}
            className={`flex items-center gap-2 px-4 py-2 font-display font-bold tracking-wider uppercase transition-all ${
              isFirstPage
                ? 'text-muted-foreground/30 cursor-not-allowed'
                : 'text-foreground border border-border hover:border-primary'
            }`}
          >
            <ChevronLeft size={16} />
            Previous
          </button>

          <span className="font-mono text-xs text-muted-foreground">
            {currentIndex + 1} / {pages.length}
          </span>

          {isLastPage ? (
            <button
              onClick={handleFinish}
              disabled={completing}
              className="flex items-center gap-2 px-6 py-2 bg-primary text-primary-foreground font-display font-bold tracking-wider uppercase hover:brightness-110 transition-all clip-sharp disabled:opacity-50"
            >
              {completing ? 'COMPLETING...' : 'COMPLETE'}
            </button>
          ) : (
            <button
              onClick={handleNext}
              disabled={completing}
              className="flex items-center gap-2 px-4 py-2 border border-primary text-primary font-display font-bold tracking-wider uppercase hover:bg-primary hover:text-primary-foreground transition-all disabled:opacity-50"
            >
              {completing ? 'LOADING...' : 'NEXT'}
              <ChevronRight size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReadingScreen;
