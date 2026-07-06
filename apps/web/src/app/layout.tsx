import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'AI Sales Lead Qualifier',
  description: 'AI-powered sales lead scoring and qualification platform',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-50 antialiased">
        <div className="min-h-screen flex">
          {/* Sidebar Navigation */}
          <aside className="w-64 bg-slate-900 text-white fixed h-full">
            <div className="p-6">
              <h1 className="text-xl font-bold">🎯 Lead Qualifier</h1>
            </div>
            <nav className="mt-6">
              <a
                href="/"
                className="flex items-center px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
              >
                📊 Dashboard
              </a>
              <a
                href="/criteria"
                className="flex items-center px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
              >
                ⚙️ Criteria
              </a>
              <a
                href="/digest"
                className="flex items-center px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
              >
                📧 Digest
              </a>
              <a
                href="/setup"
                className="flex items-center px-6 py-3 text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
              >
                🚀 Setup
              </a>
            </nav>
          </aside>

          {/* Main Content Area */}
          <main className="flex-1 ml-64 p-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
