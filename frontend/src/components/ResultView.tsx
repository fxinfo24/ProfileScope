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
          <Link to="/tasks" className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700">
            Back to Tasks
          </Link>
        </div>
      </div>
    );
  }

  if (task.status !== 'completed') {
    return (
      <div className="min-h-screen" style={{ backgroundColor: 'var(--light-bg)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="card rounded-lg p-4 mb-4 border border-yellow-400" style={{ backgroundColor: 'var(--card-bg)' }}>
            <div className="flex items-center text-yellow-700">
              <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
              <span>Task is {task.status}. Results will be available once analysis completes.</span>
            </div>
          </div>
          <Link to={`/tasks/${id}`} className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700">
            View Task Status
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
            <li><Link to={`/tasks/${id}`} className="hover:underline" style={{ color: 'var(--primary)' }}>Task #{id}</Link></li>
            <li>/</li>
            <li style={{ color: 'var(--text-primary)' }}>Results</li>
          </ol>
        </nav>

        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Analysis Results</h1>
          <div className="flex space-x-2">
            <button 
              onClick={() => handleExport('json')} 
              className="inline-flex items-center px-4 py-2 border rounded-md shadow-sm text-sm font-medium hover:opacity-80"
              style={{ 
                backgroundColor: 'var(--card-bg)', 
                borderColor: 'var(--border-color)',
                color: 'var(--text-primary)'
              }}
            >
              <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export JSON
            </button>
            <button 
              onClick={() => handleExport('pdf')} 
              className="inline-flex items-center px-4 py-2 border rounded-md shadow-sm text-sm font-medium hover:opacity-80"
              style={{ 
                backgroundColor: 'var(--card-bg)', 
                borderColor: 'var(--border-color)',
                color: 'var(--text-primary)'
              }}
            >
              <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              Export PDF
            </button>
          </div>
        </div>

        {/* Results Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Profile Information */}
          {results?.profile_info && (
            <div className="card rounded-lg shadow-sm" style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', border: '1px solid' }}>
              <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
                <h5 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Profile Information</h5>
              </div>
              <div className="p-6">
                <dl className="space-y-3">
                  {results.profile_info.username && (
                    <div className="flex justify-between">
                      <dt className="font-medium" style={{ color: 'var(--text-secondary)' }}>Username:</dt>
                      <dd className="font-semibold" style={{ color: 'var(--text-primary)' }}>@{results.profile_info.username}</dd>
                    </div>
                  )}
                  {results.profile_info.followers !== undefined && (
                    <div className="flex justify-between">
                      <dt className="font-medium" style={{ color: 'var(--text-secondary)' }}>Followers:</dt>
                      <dd className="font-semibold" style={{ color: 'var(--text-primary)' }}>{results.profile_info.followers.toLocaleString()}</dd>
                    </div>
                  )}
                  {results.profile_info.following !== undefined && (
                    <div className="flex justify-between">
                      <dt className="font-medium" style={{ color: 'var(--text-secondary)' }}>Following:</dt>
                      <dd className="font-semibold" style={{ color: 'var(--text-primary)' }}>{results.profile_info.following.toLocaleString()}</dd>
                    </div>
                  )}
                  {results.profile_info.posts !== undefined && (
                    <div className="flex justify-between">
                      <dt className="font-medium" style={{ color: 'var(--text-secondary)' }}>Posts:</dt>
                      <dd className="font-semibold" style={{ color: 'var(--text-primary)' }}>{results.profile_info.posts.toLocaleString()}</dd>
                    </div>
                  )}
                </dl>
              </div>
            </div>
          )}

          {/* Sentiment Analysis */}
          {results?.sentiment && (
            <div className="card rounded-lg shadow-sm" style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', border: '1px solid' }}>
              <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
                <h5 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Sentiment Analysis</h5>
              </div>
              <div className="p-6 space-y-4">
                {results.sentiment.overall && (
                  <div className="flex items-center space-x-2">
                    <span className="font-medium" style={{ color: 'var(--text-secondary)' }}>Overall:</span>
                    <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                      results.sentiment.overall === 'positive' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                      results.sentiment.overall === 'negative' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : 
                      'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                    }`}>
                      {results.sentiment.overall}
                    </span>
                  </div>
                )}
                {results.sentiment.positive !== undefined && (
                  <div>
                    <div className="flex justify-between mb-1">
                      <label className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Positive</label>
                      <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{results.sentiment.positive}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: `${results.sentiment.positive}%` }}></div>
                    </div>
                  </div>
                )}
                {results.sentiment.neutral !== undefined && (
                  <div>
                    <div className="flex justify-between mb-1">
                      <label className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Neutral</label>
                      <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{results.sentiment.neutral}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                      <div className="bg-gray-600 h-2 rounded-full" style={{ width: `${results.sentiment.neutral}%` }}></div>
                    </div>
                  </div>
                )}
                {results.sentiment.negative !== undefined && (
                  <div>
                    <div className="flex justify-between mb-1">
                      <label className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Negative</label>
                      <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{results.sentiment.negative}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                      <div className="bg-red-600 h-2 rounded-full" style={{ width: `${results.sentiment.negative}%` }}></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Authenticity Score */}
          {results?.authenticity && (
            <div className="card rounded-lg shadow-sm" style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', border: '1px solid' }}>
              <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
                <h5 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Authenticity Score</h5>
              </div>
              <div className="p-6">
                {results.authenticity.score !== undefined && (
                  <div className="text-center mb-4">
                    <h2 className={`text-6xl font-bold ${
                      results.authenticity.score >= 80 ? 'text-green-600' :
                      results.authenticity.score >= 50 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {results.authenticity.score}%
                    </h2>
                  </div>
                )}
                {results.authenticity.indicators && results.authenticity.indicators.length > 0 && (
                  <div>
                    <h6 className="text-sm font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Indicators:</h6>
                    <ul className="space-y-2">
                      {results.authenticity.indicators.map((indicator: string, idx: number) => (
                        <li key={idx} className="flex items-start">
                          <svg className="h-5 w-5 text-green-600 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          <span className="text-sm" style={{ color: 'var(--text-primary)' }}>{indicator}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Content Analysis */}
        {results?.content_analysis && (
          <div className="card rounded-lg shadow-sm mt-6" style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', border: '1px solid' }}>
            <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
              <h5 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Content Analysis</h5>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {results.content_analysis.topics && results.content_analysis.topics.length > 0 && (
                  <div>
                    <h6 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Topics:</h6>
                    <div className="flex flex-wrap gap-2">
                      {results.content_analysis.topics.map((topic: string, idx: number) => (
                        <span key={idx} className="px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {results.content_analysis.keywords && results.content_analysis.keywords.length > 0 && (
                  <div>
                    <h6 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Keywords:</h6>
                    <div className="flex flex-wrap gap-2">
                      {results.content_analysis.keywords.map((keyword: string, idx: number) => (
                        <span key={idx} className="px-3 py-1 text-xs font-semibold rounded-full bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200">
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {results.content_analysis.languages && results.content_analysis.languages.length > 0 && (
                  <div>
                    <h6 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Languages:</h6>
                    <div className="flex flex-wrap gap-2">
                      {results.content_analysis.languages.map((lang: string, idx: number) => (
                        <span key={idx} className="px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          {lang}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Raw Data (if no structured results) */}
        {!results?.profile_info && !results?.sentiment && (
          <div className="card rounded-lg shadow-sm mt-6" style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', border: '1px solid' }}>
            <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
              <h5 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Raw Results</h5>
            </div>
            <div className="p-6">
              <pre className="p-4 rounded overflow-x-auto text-sm" style={{ backgroundColor: 'var(--light-bg)', color: 'var(--text-primary)' }}>
                {JSON.stringify(results, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultView;
