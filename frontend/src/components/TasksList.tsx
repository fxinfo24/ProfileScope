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

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      pending: 'bg-warning',
      processing: 'bg-info',
      completed: 'bg-success',
      failed: 'bg-danger'
    };
    return badges[status] || 'bg-secondary';
  };

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Analysis Tasks</h1>
        <Link to="/dashboard" className="btn btn-primary">
          <i className="bi bi-plus-circle me-2"></i>New Analysis
        </Link>
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-4">
              <label className="form-label">Platform</label>
              <select 
                className="form-select"
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
            <div className="col-md-4">
              <label className="form-label">Status</label>
              <select 
                className="form-select"
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
      </div>

      {/* Tasks Table */}
      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : tasks.length === 0 ? (
        <div className="alert alert-info">
          <i className="bi bi-info-circle me-2"></i>
          No tasks found. Create a new analysis to get started!
        </div>
      ) : (
        <div className="card">
          <div className="table-responsive">
            <table className="table table-hover mb-0">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Platform</th>
                  <th>Profile</th>
                  <th>Status</th>
                  <th>Progress</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map(task => (
                  <tr key={task.id}>
                    <td>#{task.id}</td>
                    <td>
                      <span className="text-capitalize">{task.platform}</span>
                    </td>
                    <td>{task.profile_id}</td>
                    <td>
                      <span className={`badge ${getStatusBadge(task.status)}`}>
                        {task.status}
                      </span>
                    </td>
                    <td>
                      <div className="progress" style={{ width: '100px', height: '20px' }}>
                        <div 
                          className="progress-bar" 
                          role="progressbar" 
                          style={{ width: `${task.progress}%` }}
                          aria-valuenow={task.progress} 
                          aria-valuemin={0} 
                          aria-valuemax={100}
                        >
                          {task.progress}%
                        </div>
                      </div>
                    </td>
                    <td>{new Date(task.created_at).toLocaleDateString()}</td>
                    <td>
                      <Link 
                        to={`/tasks/${task.id}`} 
                        className="btn btn-sm btn-outline-primary"
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
  );
};

export default TasksList;
