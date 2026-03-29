import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { AxiosError } from 'axios';

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [generalError, setGeneralError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setGeneralError('');
    setLoading(true);
    try {
      await register(username, password, email || undefined);
      navigate('/');
    } catch (err) {
      const axiosErr = err as AxiosError<Record<string, string | string[]>>;
      const data = axiosErr.response?.data;
      if (data) {
        if (typeof data.detail === 'string') {
          setGeneralError(data.detail);
        } else {
          const fieldErrors: Record<string, string[]> = {};
          for (const [key, val] of Object.entries(data)) {
            fieldErrors[key] = Array.isArray(val) ? val : [String(val)];
          }
          setErrors(fieldErrors);
        }
      } else {
        setGeneralError('Registration failed.');
      }
    } finally {
      setLoading(false);
    }
  };

  const FieldError = ({ field }: { field: string }) => {
    if (!errors[field]) return null;
    return (
      <div className="text-destructive text-xs font-mono mt-1">
        {errors[field].join(', ')}
      </div>
    );
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="fixed inset-0 opacity-5" style={{
        backgroundImage: 'linear-gradient(hsl(var(--border)) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--border)) 1px, transparent 1px)',
        backgroundSize: '40px 40px',
      }} />

      <div className="relative w-full max-w-md mx-4">
        <div className="absolute -top-1 -left-1 w-6 h-6 border-t-2 border-l-2 border-primary" />
        <div className="absolute -top-1 -right-1 w-6 h-6 border-t-2 border-r-2 border-primary" />
        <div className="absolute -bottom-1 -left-1 w-6 h-6 border-b-2 border-l-2 border-primary" />
        <div className="absolute -bottom-1 -right-1 w-6 h-6 border-b-2 border-r-2 border-primary" />

        <div className="bg-card border border-border p-8">
          <div className="text-center mb-8">
            <h1 className="font-display text-4xl font-bold tracking-wider text-primary text-shadow-glow">
              LEVEL UP
            </h1>
            <div className="w-16 h-0.5 bg-primary mx-auto mt-2" />
            <p className="text-muted-foreground text-sm font-mono mt-3 tracking-widest uppercase">
              Create Account
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {generalError && (
              <div className="bg-destructive/10 border border-destructive/30 p-3 text-destructive text-sm font-mono">
                {generalError}
              </div>
            )}

            <div>
              <label className="block text-xs font-mono tracking-widest uppercase text-muted-foreground mb-2">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-background border border-border px-4 py-3 text-foreground font-mono focus:outline-none focus:border-primary transition-colors"
                required
              />
              <FieldError field="username" />
            </div>

            <div>
              <label className="block text-xs font-mono tracking-widest uppercase text-muted-foreground mb-2">
                Email <span className="text-muted-foreground/50">(optional)</span>
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-background border border-border px-4 py-3 text-foreground font-mono focus:outline-none focus:border-primary transition-colors"
              />
              <FieldError field="email" />
            </div>

            <div>
              <label className="block text-xs font-mono tracking-widest uppercase text-muted-foreground mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-background border border-border px-4 py-3 text-foreground font-mono focus:outline-none focus:border-primary transition-colors"
                required
              />
              <FieldError field="password" />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-primary-foreground py-3 font-display font-bold text-lg tracking-wider uppercase hover:brightness-110 transition-all disabled:opacity-50 clip-sharp"
            >
              {loading ? 'REGISTERING...' : 'REGISTER'}
            </button>
          </form>

          <p className="text-center text-muted-foreground text-sm mt-6 font-mono">
            Already have an account?{' '}
            <Link to="/login" className="text-primary hover:underline">
              LOGIN
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
