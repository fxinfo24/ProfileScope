// Layout Component for ProfileScope with Dark Mode
import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import {
  ChartBarIcon,
  ArrowRightOnRectangleIcon,
  MoonIcon,
  SunIcon,
} from '@heroicons/react/24/outline';
import { useTheme } from '../contexts/ThemeContext';

const Layout: React.FC = () => {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--light-bg)' }}>
      {/* Navigation */}
      <nav className="card shadow-sm border-b" style={{ borderColor: 'var(--border-color)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <div className="h-8 w-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'var(--primary)' }}>
                  <span className="text-white font-bold text-lg">P</span>
                </div>
                <span className="ml-2 text-xl font-bold" style={{ color: 'var(--text-primary)' }}>ProfileScope</span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium hover:opacity-80"
                  style={{ borderColor: 'var(--primary)', color: 'var(--text-primary)', background: 'transparent' }}
                >
                  <ChartBarIcon className="h-4 w-4 mr-2" />
                  Dashboard
                </button>
                <button
                  onClick={() => navigate('/tasks')}
                  className="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium hover:opacity-80"
                  style={{ borderColor: 'transparent', color: 'var(--text-secondary)', background: 'transparent' }}
                >
                  Tasks
                </button>
              </div>
            </div>
            <div className="ml-6 flex items-center">
              <div className="ml-3 relative">
                <div className="flex items-center space-x-4">
                  {/* Dark Mode Toggle */}
                  <button
                    onClick={toggleTheme}
                    className="p-2 rounded-full hover:opacity-80 focus:outline-none focus:ring-2 focus:ring-offset-2"
                    style={{ 
                      backgroundColor: 'var(--light-bg)', 
                      color: 'var(--text-secondary)',
                      borderColor: 'var(--border-color)',
                      border: '1px solid'
                    }}
                    title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
                    aria-label="Toggle theme"
                  >
                    {theme === 'light' ? (
                      <MoonIcon className="h-6 w-6" />
                    ) : (
                      <SunIcon className="h-6 w-6" />
                    )}
                  </button>
                  
                  <button
                    onClick={() => navigate('/dashboard')}
                    className="p-1 rounded-full hover:opacity-80 focus:outline-none focus:ring-2 focus:ring-offset-2"
                    style={{ 
                      backgroundColor: 'var(--light-bg)', 
                      color: 'var(--text-secondary)',
                      borderColor: 'var(--border-color)',
                      border: '1px solid'
                    }}
                    title="Dashboard"
                  >
                    <ArrowRightOnRectangleIcon className="h-6 w-6" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;