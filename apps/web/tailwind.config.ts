import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        admin: {
          bg: '#f5f7fb',
          surface: '#ffffff',
          soft: '#f8fafc',
          border: '#dbe4ef',
          text: '#1f2937',
          muted: '#6b7280',
          primary: '#2563eb',
          primaryDark: '#1d4ed8',
          success: '#0f766e',
          warning: '#d97706',
          danger: '#dc2626',
          sidebar: '#111827',
          sidebarSoft: '#1f2937',
        },
        slate: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        indigo: {
          600: '#4f46e5',
          700: '#4338ca',
        },
        rose: {
          50: '#fff1f2',
          100: '#ffe4e6',
          200: '#fecdd3',
          800: '#9f1239',
        },
        amber: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          800: '#92400e',
        },
        emerald: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          800: '#065f46',
        },
      },
    },
  },
  plugins: [],
};

export default config;
