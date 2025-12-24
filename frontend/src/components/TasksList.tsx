// TasksList Component - Shows all analysis tasks
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '@/services/api';

interface Task {
  id: number;
  platform: string;
  profile_id: string;
  status: string;
  progress: number;
  created_at: string;
  message?: string;
}

const TasksList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ platform: '', status: '' });

  useEffect(() => {
    loadTasks();
  }, [filter]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filter.platform) params.append('platform', filter.platform);
      if (filter.status) params.append('status', filter.status);
      
      const response = await api.getTasks(params.toString());
      setTasks(response.data.tasks || []);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      processing: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--light-bg)' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Analysis Tasks</h1>
          <Link 
            to="/dashboard" 
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Analysis
          </Link>
        </div>

        {/* Filters */}
        <div className="card rounded-lg shadow-sm mb-6 p-6" style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', border: '1px solid' }}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>Platform</label>
              <select 
                className="w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-primary-500"
                style={{ 
                  backgroundColor: 'var(--light-bg)', 
                  color: 'var(--text-primary)',
                  borderColor: 'var(--border-color)'
                }}
                value={filter.platform}
                onChange={(e) => setFilter({...filter, platform: e.target.value})}
              >
                <option value="">All Platforms</option>
                <option value="twitter">Twitter</option>
                <option value="instagram">Instagram</option>
                <option value="facebook">Facebook</option>
                <option value="linkedin">LinkedIn</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>Status</label>
              <select 
                className="w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-primary-500"
                style={{ 
                  backgroundColor: 'var(--light-bg)', 
                  color: 'var(--text-primary)',
                  borderColor: 'var(--border-color)'
                }}
                value={filter.status}
                onChange={(e) => setFilter({...filter, status: e.target.value})}
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>
        </div>

        {/* Tasks Table */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="card rounded-lg p-6 flex items-center" style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', border: '1px solid' }}>
            <svg className="h-5 w-5 mr-2" style={{ color: 'var(--primary)' }} fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <span style={{ color: 'var(--text-primary)' }}>No tasks found. Create a new analysis to get started!</span>
          </div>
        ) : (
          <div className="card rounded-lg shadow-sm overflow-hidden" style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', border: '1px solid' }}>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y" style={{ borderColor: 'var(--border-color)' }}>
                <thead style={{ backgroundColor: 'var(--light-bg)' }}>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>Platform</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>Profile</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>Progress</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>Created</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y" style={{ borderColor: 'var(--border-color)' }}>
                  {tasks.map(task => (
                    <tr key={task.id} className="hover:bg-opacity-50" style={{ backgroundColor: 'var(--card-bg)' }}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium" style={{ color: 'var(--text-primary)' }}>#{task.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm capitalize" style={{ color: 'var(--text-primary)' }}>{task.platform}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm" style={{ color: 'var(--text-primary)' }}>{task.profile_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(task.status)}`}>
                          {task.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-24 bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                            <div 
                              className="bg-primary-600 h-2 rounded-full" 
                              style={{ width: `${task.progress}%` }}
                            ></div>
                          </div>
                          <span className="ml-2 text-sm" style={{ color: 'var(--text-secondary)' }}>{task.progress}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm" style={{ color: 'var(--text-secondary)' }}>
                        {new Date(task.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <Link 
                          to={`/tasks/${task.id}`} 
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                        >
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TasksList;
