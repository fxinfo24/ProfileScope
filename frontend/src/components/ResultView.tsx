// ResultView Component - Shows detailed analysis results
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '@/services/api';

interface AnalysisResult {
  profile_info?: {
    username?: string;
    followers?: number;
    following?: number;
    posts?: number;
  };
  sentiment?: {
    overall?: string;
    positive?: number;
    negative?: number;
    neutral?: number;
  };
  content_analysis?: {
    topics?: string[];
    keywords?: string[];
    languages?: string[];
  };
  authenticity?: {
    score?: number;
    indicators?: string[];
  };
  [key: string]: any;
}

const ResultView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [task, setTask] = useState<any>(null);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadResults();
  }, [id]);

  const loadResults = async () => {
    try {
      setLoading(true);
      const taskResponse = await api.getTask(Number(id));
      setTask(taskResponse.data);

      if (taskResponse.data.status === 'completed') {
        const resultsResponse = await api.getTaskResults(Number(id));
        setResults(resultsResponse.data);
      }
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format: string) => {
    window.open(`/api/tasks/${id}/export?format=${format}`, '_blank');
  };

  if (loading) {
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

  if (task.status !== 'completed') {
    return (
      <div className="container mt-4">
        <div className="alert alert-warning">
          <i className="bi bi-hourglass-split me-2"></i>
          Task is {task.status}. Results will be available once analysis completes.
        </div>
        <Link to={`/tasks/${id}`} className="btn btn-primary">View Task Status</Link>
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
          <li className="breadcrumb-item"><Link to={`/tasks/${id}`}>Task #{id}</Link></li>
          <li className="breadcrumb-item active">Results</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Analysis Results</h1>
        <div className="btn-group">
          <button 
            onClick={() => handleExport('json')} 
            className="btn btn-outline-secondary"
          >
            <i className="bi bi-download me-2"></i>Export JSON
          </button>
          <button 
            onClick={() => handleExport('pdf')} 
            className="btn btn-outline-secondary"
          >
            <i className="bi bi-file-pdf me-2"></i>Export PDF
          </button>
        </div>
      </div>

      {/* Results Grid */}
      <div className="row">
        {/* Profile Information */}
        {results?.profile_info && (
          <div className="col-md-4 mb-4">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Profile Information</h5>
              </div>
              <div className="card-body">
                <table className="table table-sm">
                  <tbody>
                    {results.profile_info.username && (
                      <tr>
                        <th>Username:</th>
                        <td>@{results.profile_info.username}</td>
                      </tr>
                    )}
                    {results.profile_info.followers !== undefined && (
                      <tr>
                        <th>Followers:</th>
                        <td>{results.profile_info.followers.toLocaleString()}</td>
                      </tr>
                    )}
                    {results.profile_info.following !== undefined && (
                      <tr>
                        <th>Following:</th>
                        <td>{results.profile_info.following.toLocaleString()}</td>
                      </tr>
                    )}
                    {results.profile_info.posts !== undefined && (
                      <tr>
                        <th>Posts:</th>
                        <td>{results.profile_info.posts.toLocaleString()}</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Sentiment Analysis */}
        {results?.sentiment && (
          <div className="col-md-4 mb-4">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Sentiment Analysis</h5>
              </div>
              <div className="card-body">
                {results.sentiment.overall && (
                  <div className="mb-3">
                    <strong>Overall: </strong>
                    <span className={`badge ${
                      results.sentiment.overall === 'positive' ? 'bg-success' :
                      results.sentiment.overall === 'negative' ? 'bg-danger' : 'bg-secondary'
                    }`}>
                      {results.sentiment.overall}
                    </span>
                  </div>
                )}
                {results.sentiment.positive !== undefined && (
                  <div className="mb-2">
                    <label>Positive: {results.sentiment.positive}%</label>
                    <div className="progress">
                      <div 
                        className="progress-bar bg-success" 
                        style={{ width: `${results.sentiment.positive}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                {results.sentiment.neutral !== undefined && (
                  <div className="mb-2">
                    <label>Neutral: {results.sentiment.neutral}%</label>
                    <div className="progress">
                      <div 
                        className="progress-bar bg-secondary" 
                        style={{ width: `${results.sentiment.neutral}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                {results.sentiment.negative !== undefined && (
                  <div className="mb-2">
                    <label>Negative: {results.sentiment.negative}%</label>
                    <div className="progress">
                      <div 
                        className="progress-bar bg-danger" 
                        style={{ width: `${results.sentiment.negative}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Authenticity Score */}
        {results?.authenticity && (
          <div className="col-md-4 mb-4">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Authenticity Score</h5>
              </div>
              <div className="card-body">
                {results.authenticity.score !== undefined && (
                  <div className="text-center mb-3">
                    <h2 className={`display-4 ${
                      results.authenticity.score >= 80 ? 'text-success' :
                      results.authenticity.score >= 50 ? 'text-warning' : 'text-danger'
                    }`}>
                      {results.authenticity.score}%
                    </h2>
                  </div>
                )}
                {results.authenticity.indicators && results.authenticity.indicators.length > 0 && (
                  <div>
                    <h6>Indicators:</h6>
                    <ul className="list-unstyled">
                      {results.authenticity.indicators.map((indicator: string, idx: number) => (
                        <li key={idx} className="mb-1">
                          <i className="bi bi-check-circle text-success me-2"></i>
                          {indicator}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Content Analysis */}
        {results?.content_analysis && (
          <div className="col-12 mb-4">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Content Analysis</h5>
              </div>
              <div className="card-body">
                <div className="row">
                  {results.content_analysis.topics && results.content_analysis.topics.length > 0 && (
                    <div className="col-md-4">
                      <h6>Topics:</h6>
                      <div className="d-flex flex-wrap gap-2">
                        {results.content_analysis.topics.map((topic: string, idx: number) => (
                          <span key={idx} className="badge bg-primary">{topic}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {results.content_analysis.keywords && results.content_analysis.keywords.length > 0 && (
                    <div className="col-md-4">
                      <h6>Keywords:</h6>
                      <div className="d-flex flex-wrap gap-2">
                        {results.content_analysis.keywords.map((keyword: string, idx: number) => (
                          <span key={idx} className="badge bg-info">{keyword}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {results.content_analysis.languages && results.content_analysis.languages.length > 0 && (
                    <div className="col-md-4">
                      <h6>Languages:</h6>
                      <div className="d-flex flex-wrap gap-2">
                        {results.content_analysis.languages.map((lang: string, idx: number) => (
                          <span key={idx} className="badge bg-success">{lang}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Raw Data (if no structured results) */}
        {!results?.profile_info && !results?.sentiment && (
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Raw Results</h5>
              </div>
              <div className="card-body">
                <pre className="bg-light p-3 rounded">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultView;
