'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Target,
  LayoutDashboard,
  SlidersHorizontal,
  Mail,
  Rocket,
  Search,
  Bell,
  Moon,
  Sun,
  Menu,
  ChevronDown,
} from 'lucide-react';

const NAV = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/criteria', label: 'Criteria', icon: SlidersHorizontal },
  { href: '/digest', label: 'Digest', icon: Mail },
  { href: '/setup', label: 'Setup', icon: Rocket },
];

function isActive(pathname: string, href: string) {
  if (href === '/') return pathname === '/' || pathname.startsWith('/leads');
  return pathname === href || pathname.startsWith(href + '/');
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false); // mobile sidebar
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('cortex-theme');
    const isDark = saved === 'dark';
    setDark(isDark);
    document.documentElement.dataset.theme = isDark ? 'dark' : 'light';
  }, []);

  useEffect(() => {
    setOpen(false); // close mobile drawer on navigation
  }, [pathname]);

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.dataset.theme = next ? 'dark' : 'light';
    localStorage.setItem('cortex-theme', next ? 'dark' : 'light');
  };

  return (
    <div className="min-h-screen">
      {/* mobile backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          onClick={() => setOpen(false)}
          aria-hidden
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-admin-sidebar text-slate-100 transition-transform duration-200 lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center gap-3 px-5 py-5">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-[#2563eb] to-[#0f766e] text-white shadow-lg">
            <Target className="h-5 w-5" />
          </span>
          <span className="leading-tight">
            <span className="block text-sm font-bold">Cortex</span>
            <span className="block text-[11px] text-slate-400">Lead Qualifier</span>
          </span>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-2">
          {NAV.map(({ href, label, icon: Icon }) => (
            <Link key={href} href={href} className={`side-link ${isActive(pathname, href) ? 'active' : ''}`}>
              <Icon className="h-[18px] w-[18px]" />
              <span>{label}</span>
            </Link>
          ))}
        </nav>

        <div className="mx-3 mb-2 flex items-center gap-3 rounded-lg bg-admin-sidebarSoft px-3 py-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-[#2563eb] to-[#0f766e] text-xs font-bold text-white">
            SC
          </span>
          <span className="leading-tight">
            <span className="block text-sm font-semibold text-white">Sales Cortex</span>
            <span className="block text-[11px] text-slate-400">Active workspace</span>
          </span>
        </div>

        <div className="flex items-center gap-2 px-5 py-3 text-[11px] text-slate-400">
          <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_0_3px_rgba(52,211,153,0.25)]" />
          Pipeline running smoothly
        </div>
      </aside>

      {/* Main column */}
      <div className="lg:pl-64">
        {/* Topbar */}
        <header
          className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b bg-admin-surface px-4 lg:px-6"
          style={{ borderColor: 'var(--admin-border)' }}
        >
          <button
            className="rounded-md p-2 text-admin-muted hover:bg-admin-soft lg:hidden"
            onClick={() => setOpen(true)}
            aria-label="Open sidebar"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="relative hidden max-w-md flex-1 md:block">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-admin-muted" />
            <input
              type="search"
              placeholder="Search leads, companies, reports"
              className="w-full rounded-lg border bg-admin-soft py-2 pl-9 pr-3 text-sm outline-none focus:border-admin-primary"
              style={{ borderColor: 'var(--admin-border)', color: 'var(--admin-text)' }}
            />
          </div>

          <div className="ml-auto flex items-center gap-1.5">
            <button
              onClick={toggleTheme}
              className="rounded-lg p-2 text-admin-muted hover:bg-admin-soft"
              aria-label="Toggle theme"
              title="Toggle theme"
            >
              {dark ? <Sun className="h-[18px] w-[18px]" /> : <Moon className="h-[18px] w-[18px]" />}
            </button>
            <button className="relative rounded-lg p-2 text-admin-muted hover:bg-admin-soft" aria-label="Notifications">
              <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-admin-danger" />
              <Bell className="h-[18px] w-[18px]" />
            </button>
            <button className="ml-1 flex items-center gap-2 rounded-lg py-1 pl-1 pr-2 hover:bg-admin-soft">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-[#2563eb] to-[#0f766e] text-xs font-bold text-white">
                SC
              </span>
              <span className="hidden text-sm font-medium sm:inline" style={{ color: 'var(--admin-text)' }}>
                Sales Cortex
              </span>
              <ChevronDown className="hidden h-4 w-4 text-admin-muted sm:inline" />
            </button>
          </div>
        </header>

        <main className="px-4 py-6 lg:px-6">{children}</main>

        <footer className="px-4 pb-6 pt-2 text-center text-xs text-admin-muted lg:px-6">
          Cortex — AI Sales Lead Qualifier · Dashboard styled after adminHMD
        </footer>
      </div>
    </div>
  );
}
