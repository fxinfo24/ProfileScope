// TaskView Component - Shows detailed view of a single task
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '@/services/api';

interface Task {
  id: number;
  platform: string;
  profile_id: string;
  status: string;
  progress: number;
  message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  duration?: number;
  error?: string;
}

const TaskView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTask();
    // Poll for updates if task is not completed
    const interval = setInterval(() => {
      if (task && (task.status === 'pending' || task.status === 'processing')) {
        loadTask();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [id, task?.status]);

  const loadTask = async () => {
    try {
      setLoading(true);
      const response = await api.getTask(Number(id));
      setTask(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load task');
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async () => {
    try {
      await api.retryTask(Number(id));
      loadTask();
    } catch (err) {
      console.error('Failed to retry task:', err);
    }
  };

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel this task?')) return;
    try {
      await api.cancelTask(Number(id));
      loadTask();
    } catch (err) {
      console.error('Failed to cancel task:', err);
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

  if (loading && !task) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--light-bg)' }}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="min-h-screen" style={{ backgroundColor: 'var(--light-bg)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="card rounded-lg p-4 mb-4 border border-red-400" style={{ backgroundColor: 'var(--card-bg)' }}>
            <div className="flex items-center text-red-600">
              <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>{error || 'Task not found'}</span>
            </div>
          </div>
          <Link 
            to="/tasks" 
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
          >
            Back to Tasks
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--light-bg)' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="mb-6">
          <ol className="flex items-center space-x-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
            <li><Link to="/dashboard" className="hover:underline" style={{ color: 'var(--primary)' }}>Dashboard</Link></li>
            <li>/</li>
            <li><Link to="/tasks" className="hover:underline" style={{ color: 'var(--primary)' }}>Tasks</Link></li>
            <li>/</li>
            <li style={{ color: 'var(--text-primary)' }}>Task #{task.id}</li>
          </ol>
        </nav>

        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Task #{task.id}</h1>
          <div className="flex space-x-2">
            {task.status === 'completed' && (
              <Link 
                to={`/tasks/${task.id}/results`} 
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
              >
                <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                View Results
              </Link>
            )}
            {(task.status === 'pending' || task.status === 'failed') && (
              <button 
                onClick={handleRetry} 
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-yellow-600 hover:bg-yellow-700"
              >
                <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Retry
              </button>
            )}
            {(task.status === 'pending' || task.status === 'processing') && (
              <button 
                onClick={handleCancel} 
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
              >
                <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Cancel
              </button>
            )}
          </div>
        </div>

        {/* Status Card */}
        <div className="card rounded-lg shadow-sm mb-6" style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', border: '1px solid' }}>
          <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
            <h5 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Task Status</h5>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-center">
                <span className={`px-4 py-2 text-lg font-semibold rounded-full ${getStatusColor(task.status)}`}>
                  {task.status.toUpperCase()}
                </span>
              </div>
              <div>
                <div className="w-full bg-gray-200 rounded-full h-8 dark:bg-gray-700">
                  <div 
                    className="bg-primary-600 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium transition-all duration-300" 
                    style={{ width: `${task.progress}%` }}
                  >
                    {task.progress}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card rounded-lg shadow-sm" style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', border: '1px solid' }}>
            <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
              <h6 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>Task Details</h6>
            </div>
            <div className="p-6">
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="font-medium" style={{ color: 'var(--text-secondary)' }}>Task ID:</dt>
                  <dd className="font-semibold" style={{ color: 'var(--text-primary)' }}>{task.id}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium" style={{ color: 'var(--text-secondary)' }}>Platform:</dt>
                  <dd className="font-semibold capitalize" style={{ color: 'var(--text-primary)' }}>{task.platform}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium" style={{ color: 'var(--text-secondary)' }}>Profile ID:</dt>
                  <dd className="font-semibold" style={{ color: 'var(--text-primary)' }}>{task.profile_id}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium" style={{ color: 'var(--text-secondary)' }}>Created:</dt>
                  <dd className="text-sm" style={{ color: 'var(--text-primary)' }}>{new Date(task.created_at).toLocaleString()}</dd>
                </div>
                {task.started_at && (
                  <div className="flex justify-between">
                    <dt className="font-medium" style={{ color: 'var(--text-secondary)' }}>Started:</dt>
                    <dd className="text-sm" style={{ color: 'var(--text-primary)' }}>{new Date(task.started_at).toLocaleString()}</dd>
                  </div>
                )}
                {task.completed_at && (
                  <div className="flex justify-between">
                    <dt className="font-medium" style={{ color: 'var(--text-secondary)' }}>Completed:</dt>
                    <dd className="text-sm" style={{ color: 'var(--text-primary)' }}>{new Date(task.completed_at).toLocaleString()}</dd>
                  </div>
                )}
                {task.duration && (
                  <div className="flex justify-between">
                    <dt className="font-medium" style={{ color: 'var(--text-secondary)' }}>Duration:</dt>
                    <dd className="font-semibold" style={{ color: 'var(--text-primary)' }}>{task.duration.toFixed(2)}s</dd>
                  </div>
                )}
              </dl>
            </div>
          </div>

          <div className="card rounded-lg shadow-sm" style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', border: '1px solid' }}>
            <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
              <h6 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>Current Operation</h6>
            </div>
            <div className="p-6">
              {task.message ? (
                <div className="flex items-start">
                  <svg className="h-5 w-5 mr-3 flex-shrink-0" style={{ color: 'var(--primary)' }} fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <p style={{ color: 'var(--text-primary)' }}>{task.message}</p>
                </div>
              ) : task.status === 'pending' ? (
                <div className="flex items-center">
                  <svg className="h-5 w-5 mr-3" style={{ color: 'var(--text-secondary)' }} fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                  </svg>
                  <p style={{ color: 'var(--text-primary)' }}>Initializing...</p>
                </div>
              ) : task.status === 'processing' ? (
                <div className="flex items-center">
                  <svg className="animate-spin h-5 w-5 mr-3" style={{ color: 'var(--primary)' }} fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p style={{ color: 'var(--text-primary)' }}>Processing analysis...</p>
                </div>
              ) : task.status === 'completed' ? (
                <div className="flex items-center text-green-600">
                  <svg className="h-5 w-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <p>Analysis completed successfully!</p>
                </div>
              ) : task.error ? (
                <div className="flex items-start text-red-600">
                  <svg className="h-5 w-5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <p>{task.error}</p>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskView;
