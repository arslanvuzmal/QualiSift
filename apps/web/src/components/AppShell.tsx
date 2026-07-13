'use client';

import { useState } from 'react';
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
  Menu,
  LogOut,
  ChevronRight
} from 'lucide-react';
import { Toaster } from 'sonner';

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
  const [open, setOpen] = useState(false);

  // Generate breadcrumb based on path
  const getBreadcrumb = () => {
    if (pathname === '/') return 'Dashboard';
    if (pathname.startsWith('/leads/')) return 'Lead Detail';
    if (pathname === '/criteria') return 'Criteria Configuration';
    if (pathname === '/digest') return 'Digest';
    if (pathname === '/setup') return 'Setup Wizard';
    return 'Overview';
  };

  return (
    <div className="min-h-screen bg-slate-950">
      <Toaster position="top-right" richColors />
      
      {/* mobile backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-slate-900/40 lg:hidden"
          onClick={() => setOpen(false)}
          aria-hidden
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-slate-950 border-r border-slate-800 text-slate-100 transition-transform duration-200 lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <Link href="/" className="flex items-center gap-3 px-5 py-5 transition-opacity hover:opacity-80">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-[#333333] to-[#000000] text-white shadow-[0_0_15px_rgba(255,255,255,0.1)] border border-white/10">
            <Target className="h-5 w-5" />
          </span>
          <span className="leading-tight">
            <span className="block text-sm font-bold tracking-tight">Cortex</span>
            <span className="block text-[11px] text-slate-500 font-bold uppercase tracking-tighter">Lead Qualifier</span>
          </span>
        </Link>
        <div className="flex items-center gap-3 px-6 py-6">
          <span className="flex h-8 w-8 items-center justify-center rounded bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-sm">
            <Target className="h-5 w-5" />
          </span>
          <span className="font-bold tracking-tight text-white text-lg">CORTEX</span>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-2">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = isActive(pathname, href);
            return (
              <Link
                key={href}
                href={href}
                onClick={() => setOpen(false)}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 ease-out ${
                  active
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
                }`}
              >
                <Icon className="h-5 w-5" />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="mx-3 mb-2 flex items-center gap-3 rounded-xl bg-admin-sidebarSoft px-3 py-3 border border-white/5 shadow-inner">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-[#444] to-[#111] text-xs font-black text-white border border-white/10">
            SC
          </span>
          <span className="leading-tight">
            <span className="block text-sm font-bold text-white">Sales Cortex</span>
            <span className="block text-[11px] text-slate-500 font-bold">Active workspace</span>
          </span>
        </div>

        <div className="flex items-center gap-2 px-5 py-3 text-[10px] font-black uppercase tracking-widest text-slate-500">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
          System Operational
        <div className="p-4">
          <div className="flex items-center gap-3 rounded-xl bg-slate-800 p-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-sm font-bold text-white">
              JD
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-sm font-medium text-white">Jane Doe</p>
              <p className="truncate text-xs text-slate-400">jane@cortex.ai</p>
            </div>
            <button className="text-slate-400 hover:text-white transition-colors" title="Logout">
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main column */}
      <div className="lg:pl-64 flex flex-col min-h-screen">
        {/* Topbar */}
        <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-slate-800 bg-slate-950/80 px-4 backdrop-blur-md lg:px-8">
          <button
            className="rounded-md p-2 text-slate-400 hover:bg-slate-900 lg:hidden"
            onClick={() => setOpen(true)}
            aria-label="Open sidebar"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex items-center gap-2 text-sm text-slate-400">
            <span className="font-medium text-slate-100">CORTEX</span>
            <ChevronRight className="h-4 w-4 text-slate-600" />
            <span className="text-slate-500">{getBreadcrumb()}</span>
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
            <button className="ml-1 flex items-center gap-2 rounded-xl py-1 pl-1 pr-2 hover:bg-white/5 border border-transparent hover:border-white/10 transition-all">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-[#444] to-[#111] text-xs font-black text-white border border-white/10">
                SC
              </span>
              <span className="hidden text-sm font-bold sm:inline" style={{ color: 'var(--admin-text)' }}>
                Sales Cortex
              </span>
              <ChevronDown className="hidden h-4 w-4 text-admin-muted sm:inline" />
          <div className="ml-auto flex items-center gap-4">
            <div className="relative hidden w-64 md:block">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <input
                type="search"
                placeholder="Search leads... (Cmd+K)"
                className="w-full rounded-lg border border-slate-800 bg-slate-900 py-1.5 pl-9 pr-3 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
              />
            </div>
            
            <button className="relative rounded-lg p-2 text-slate-400 hover:bg-slate-900 transition-colors">
              <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-rose-500 ring-2 ring-slate-950" />
              <Bell className="h-5 w-5" />
            </button>
          </div>
        </header>

        <main className="flex-1 p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
