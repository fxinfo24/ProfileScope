// Premium Glass Layout Component
import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  ChartBarIcon,
  ListBulletIcon,
} from '@heroicons/react/24/outline';

const Layout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen relative overflow-hidden font-sans text-white">
      {/* Ambient background glow effects */}
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-500/20 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary-500/20 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '1.5s' }} />
      </div>

      {/* Floating Glass Navigation */}
      <nav className="fixed top-4 left-1/2 -translate-x-1/2 w-[95%] max-w-7xl z-50 transition-all duration-300">
        <div className="glass-panel rounded-2xl px-6 py-3 flex items-center justify-between">

          {/* Logo Area */}
          <div className="flex items-center space-x-3 cursor-pointer group" onClick={() => navigate('/')}>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-primary-500 to-secondary-500 rounded-full blur opacity-75 group-hover:opacity-100 transition duration-1000"></div>
              <img
                src="/logo.png"
                alt="Vanta Logo"
                className="relative h-10 w-10 rounded-full object-cover border border-white/10 group-hover:scale-105 transition-transform duration-300 shadow-lg"
              />
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70 tracking-tight font-display">
              Vanta
            </span>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1 bg-black/20 rounded-xl p-1 border border-white/5">
            <button
              onClick={() => navigate('/dashboard')}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${isActive('/dashboard') || isActive('/')
                ? 'bg-primary-500/20 text-white shadow-[0_0_20px_rgba(99,102,241,0.3)] border border-primary-500/30'
                : 'text-white/60 hover:text-white hover:bg-white/5'
                }`}
            >
              <ChartBarIcon className="h-4 w-4 mr-2" />
              Dashboard
            </button>
            <button
              onClick={() => navigate('/tasks')}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${isActive('/tasks')
                ? 'bg-primary-500/20 text-white shadow-[0_0_20px_rgba(99,102,241,0.3)] border border-primary-500/30'
                : 'text-white/60 hover:text-white hover:bg-white/5'
                }`}
            >
              <ListBulletIcon className="h-4 w-4 mr-2" />
              Tasks
            </button>
          </div>

          {/* Right Actions */}
          <div className="flex items-center space-x-4">
            <div className="h-8 w-[1px] bg-white/10 hidden sm:block"></div>
            <div className="flex items-center space-x-3">
              <div className="px-3 py-1.5 rounded-full bg-primary-500/10 border border-primary-500/20 flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse shadow-[0_0_10px_#4ade80]" />
                <span className="text-xs font-medium text-primary-200">System Online</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="pt-28 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto min-h-screen relative z-0">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;