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

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      pending: 'bg-warning text-dark',
      processing: 'bg-info text-dark',
      completed: 'bg-success',
      failed: 'bg-danger'
    };
    return badges[status] || 'bg-secondary';
  };

  if (loading && !task) {
    return (
      <div className="container mt-4">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="container mt-4">
        <div className="alert alert-danger">
          <i className="bi bi-exclamation-triangle me-2"></i>
          {error || 'Task not found'}
        </div>
        <Link to="/tasks" className="btn btn-primary">Back to Tasks</Link>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      {/* Breadcrumb */}
      <nav aria-label="breadcrumb" className="mb-4">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
          <li className="breadcrumb-item"><Link to="/tasks">Tasks</Link></li>
          <li className="breadcrumb-item active">Task #{task.id}</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Task #{task.id}</h1>
        <div className="btn-group">
          {task.status === 'completed' && (
            <Link 
              to={`/tasks/${task.id}/results`} 
              className="btn btn-primary"
            >
              <i className="bi bi-bar-chart me-2"></i>View Results
            </Link>
          )}
          {(task.status === 'pending' || task.status === 'failed') && (
            <button onClick={handleRetry} className="btn btn-warning">
              <i className="bi bi-arrow-clockwise me-2"></i>Retry
            </button>
          )}
          {(task.status === 'pending' || task.status === 'processing') && (
            <button onClick={handleCancel} className="btn btn-danger">
              <i className="bi bi-x-circle me-2"></i>Cancel
            </button>
          )}
        </div>
      </div>

      {/* Status Card */}
      <div className="card mb-4">
        <div className="card-header">
          <h5 className="mb-0">Task Status</h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-6">
              <span className={`badge ${getStatusBadge(task.status)} fs-5`}>
                {task.status.toUpperCase()}
              </span>
            </div>
            <div className="col-md-6 text-end">
              <div className="progress" style={{ height: '30px' }}>
                <div 
                  className="progress-bar progress-bar-striped progress-bar-animated" 
                  role="progressbar" 
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
      <div className="row">
        <div className="col-md-6">
          <div className="card mb-4">
            <div className="card-header">
              <h6 className="mb-0">Task Details</h6>
            </div>
            <div className="card-body">
              <table className="table table-sm">
                <tbody>
                  <tr>
                    <th>Task ID:</th>
                    <td>{task.id}</td>
                  </tr>
                  <tr>
                    <th>Platform:</th>
                    <td className="text-capitalize">{task.platform}</td>
                  </tr>
                  <tr>
                    <th>Profile ID:</th>
                    <td>{task.profile_id}</td>
                  </tr>
                  <tr>
                    <th>Created:</th>
                    <td>{new Date(task.created_at).toLocaleString()}</td>
                  </tr>
                  {task.started_at && (
                    <tr>
                      <th>Started:</th>
                      <td>{new Date(task.started_at).toLocaleString()}</td>
                    </tr>
                  )}
                  {task.completed_at && (
                    <tr>
                      <th>Completed:</th>
                      <td>{new Date(task.completed_at).toLocaleString()}</td>
                    </tr>
                  )}
                  {task.duration && (
                    <tr>
                      <th>Duration:</th>
                      <td>{task.duration.toFixed(2)}s</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card mb-4">
            <div className="card-header">
              <h6 className="mb-0">Current Operation</h6>
            </div>
            <div className="card-body">
              {task.message ? (
                <p className="mb-0">
                  <i className="bi bi-info-circle me-2"></i>
                  {task.message}
                </p>
              ) : task.status === 'pending' ? (
                <p className="mb-0">
                  <i className="bi bi-hourglass-split me-2"></i>
                  Initializing...
                </p>
              ) : task.status === 'processing' ? (
                <p className="mb-0">
                  <i className="bi bi-gear-fill me-2 spin"></i>
                  Processing analysis...
                </p>
              ) : task.status === 'completed' ? (
                <p className="mb-0 text-success">
                  <i className="bi bi-check-circle me-2"></i>
                  Analysis completed successfully!
                </p>
              ) : task.error ? (
                <p className="mb-0 text-danger">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  {task.error}
                </p>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskView;
