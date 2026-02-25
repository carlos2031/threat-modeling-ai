import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, Menu, Bell } from 'lucide-react';
import { useNotifications } from '../hooks/useNotifications';

interface HeaderProps {
  sidebarOpen?: boolean;
  onToggleSidebar?: () => void;
}

export function Header({ onToggleSidebar }: HeaderProps) {
  const { data } = useNotifications();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

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

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/50 bg-slate-950/80 backdrop-blur-xl">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between max-w-7xl">
        <div className="flex items-center gap-3">
          {onToggleSidebar && (
            <button
              type="button"
              onClick={onToggleSidebar}
              className="lg:hidden p-2 text-gray-400 hover:text-white"
              aria-label="Menu"
            >
              <Menu className="w-6 h-6" />
            </button>
          )}
          <Link to="/" className="flex items-center gap-3">
            <ShieldAlert className="text-indigo-500 w-10 h-10" />
            <div>
              <h1 className="text-xl font-bold tracking-tight">CloudSec AI</h1>
              <p className="text-gray-400 text-xs">
                STRIDE/DREAD para diagramas de arquitetura
              </p>
            </div>
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <Link
            to="/analyses"
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            Análises
          </Link>

          <div className="relative" ref={dropdownRef}>
            <button
              type="button"
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="relative p-2 text-gray-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
              aria-label="Notificações"
            >
              <Bell className="w-6 h-6" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] flex items-center justify-center bg-red-500 text-white text-xs font-bold rounded-full px-1">
                  {unreadCount > 99 ? '99+' : unreadCount}
                </span>
              )}
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-80 glass-card py-2 z-50 max-h-96 overflow-y-auto">
                <div className="px-4 py-2 border-b border-white/10">
                  <h3 className="font-semibold text-sm">
                    Notificações {unreadCount > 0 && `(${unreadCount})`}
                  </h3>
                </div>
                {notifications.length === 0 ? (
                  <p className="px-4 py-6 text-sm text-gray-500">
                    Nenhuma notificação nova
                  </p>
                ) : (
                  <ul className="py-2">
                    {notifications.map((n) => (
                      <li key={n.id}>
                        <Link
                          to={n.link.startsWith('/') ? n.link : `/${n.link}`}
                          onClick={() => setDropdownOpen(false)}
                          className="block px-4 py-3 hover:bg-white/5 transition-colors"
                        >
                          <p className="font-medium text-sm">{n.title}</p>
                          <p className="text-xs text-gray-500 line-clamp-2">
                            {n.message}
                          </p>
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
                {notifications.length > 0 && (
                  <Link
                    to="/analyses"
                    onClick={() => setDropdownOpen(false)}
                    className="block px-4 py-2 text-center text-sm text-indigo-400 hover:text-indigo-300"
                  >
                    Ver todas as análises
                  </Link>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
