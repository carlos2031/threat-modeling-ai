import { useState, useRef, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldAlert, Bell, LayoutList, Home } from 'lucide-react';
import { useNotifications } from '../hooks/useNotifications';

export function Header() {
  const { data, markRead } = useNotifications();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const location = useLocation();

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const unreadCount = data?.unread_count ?? 0;
  const notifications = data?.notifications ?? [];

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/50 bg-slate-950/90 backdrop-blur-xl">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between max-w-6xl">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="bg-indigo-500/10 p-2 rounded-xl group-hover:bg-indigo-500/20 transition-colors">
            <ShieldAlert className="text-indigo-400 w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">CloudSec AI</h1>
            <p className="text-gray-500 text-[11px] hidden sm:block">Threat Modeling · STRIDE/DREAD</p>
          </div>
        </Link>

        <nav className="flex items-center gap-1">
          <Link
            to="/"
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-colors ${
              isActive('/') ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Home className="w-4 h-4" />
            <span className="hidden sm:inline">Início</span>
          </Link>

          <Link
            to="/analyses"
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-colors ${
              location.pathname.startsWith('/analyses') ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <LayoutList className="w-4 h-4" />
            <span className="hidden sm:inline">Análises</span>
          </Link>

          <div className="relative ml-1" ref={dropdownRef}>
            <button
              type="button"
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="relative p-2 text-gray-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
              aria-label="Notificações"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center bg-red-500 text-white text-[10px] font-bold rounded-full px-1">
                  {unreadCount > 99 ? '99+' : unreadCount}
                </span>
              )}
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-slate-900 border border-white/10 rounded-xl shadow-2xl py-1 z-50 max-h-96 overflow-y-auto">
                <div className="px-4 py-2.5 border-b border-white/10">
                  <h3 className="font-semibold text-sm">
                    Notificações {unreadCount > 0 && <span className="text-indigo-400">({unreadCount})</span>}
                  </h3>
                </div>
                {notifications.length === 0 ? (
                  <p className="px-4 py-8 text-sm text-gray-500 text-center">
                    Nenhuma notificação
                  </p>
                ) : (
                  <ul className="py-1">
                    {notifications.map((n) => (
                      <li key={n.id}>
                        <Link
                          to={n.link.startsWith('/') ? n.link : `/${n.link}`}
                          onClick={() => {
                            markRead(n.id);
                            setDropdownOpen(false);
                          }}
                          className="block px-4 py-3 hover:bg-white/5 transition-colors"
                        >
                          <p className="font-medium text-sm">{n.title}</p>
                          <p className="text-xs text-gray-500 line-clamp-2 mt-0.5">{n.message}</p>
                          <p className="text-[10px] text-gray-600 mt-1">
                            {new Date(n.created_at).toLocaleString('pt-BR')}
                          </p>
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        </nav>
      </div>
    </header>
  );
}
