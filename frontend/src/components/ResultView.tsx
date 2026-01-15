// ResultView Component - Premium Glass UI
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '@/services/api';
import {
  ArrowDownTrayIcon,
  UserIcon,
  ChatBubbleLeftRightIcon,
  ShieldCheckIcon,
  HashtagIcon,
  LanguageIcon,
} from '@heroicons/react/24/outline';

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
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="relative">
          <div className="absolute inset-0 bg-secondary-500/20 blur-xl rounded-full"></div>
          <div className="relative animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-secondary-500"></div>
        </div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="glass-panel p-8 rounded-2xl text-center max-w-lg mx-auto mt-20">
        <h2 className="text-xl font-bold text-white mb-2">Unavailable</h2>
        <p className="text-white/60 mb-6">{error || 'Task not found'}</p>
        <Link to="/tasks" className="text-primary-400 hover:text-primary-300">Return to Tasks</Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in-up pb-12">
      {/* Header */}
      <div className="glass-panel p-8 rounded-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-secondary-500/10 rounded-full blur-[100px] -mr-20 -mt-20 pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 text-white/40 text-sm mb-2">
              <span className="uppercase tracking-wider">Analysis Report</span>
              <span>•</span>
              <span className="font-mono">#{id}</span>
            </div>
            <h1 className="text-4xl font-bold text-white font-display mb-2">
              Deep Profile Analysis
            </h1>
            <p className="text-lg text-white/60">
              Intelligence report for <span className="text-white font-medium">@{task.profile_id}</span> on <span className="capitalize">{task.platform}</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => handleExport('json')}
              className="glass-button bg-white/5 hover:bg-white/10 text-white flex items-center"
            >
              <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
              JSON
            </button>
            <button
              onClick={() => handleExport('pdf')}
              className="glass-button bg-primary-600 hover:bg-primary-500 text-white flex items-center shadow-[0_0_15px_rgba(99,102,241,0.3)]"
            >
              <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
              Export Report
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Profile Card */}
        <div className="glass-card p-6 rounded-2xl group hover:bg-white/5 transition-all duration-500">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-xl bg-blue-500/20 text-blue-400">
              <UserIcon className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold text-white">Identity</h3>
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 rounded-lg bg-white/5">
              <span className="text-white/60">Followers</span>
              <span className="text-white font-mono font-bold text-lg">{results?.profile_info?.followers?.toLocaleString() ?? '-'}</span>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-white/5">
              <span className="text-white/60">Following</span>
              <span className="text-white font-mono font-bold text-lg">{results?.profile_info?.following?.toLocaleString() ?? '-'}</span>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-white/5">
              <span className="text-white/60">Posts</span>
              <span className="text-white font-mono font-bold text-lg">{results?.profile_info?.posts?.toLocaleString() ?? '-'}</span>
            </div>
          </div>
        </div>

        {/* Authenticity Card */}
        <div className="glass-card p-6 rounded-2xl group hover:bg-white/5 transition-all duration-500 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent pointer-events-none"></div>
          <div className="flex items-center gap-3 mb-6 relative z-10">
            <div className="p-3 rounded-xl bg-emerald-500/20 text-emerald-400">
              <ShieldCheckIcon className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold text-white">Trust Score</h3>
          </div>

          <div className="flex flex-col items-center justify-center py-6">
            <div className="relative">
              <svg className="w-32 h-32 transform -rotate-90">
                <circle cx="64" cy="64" r="60" stroke="currentColor" strokeWidth="8" className="text-white/5" fill="none" />
                <circle
                  cx="64" cy="64" r="60" stroke="currentColor" strokeWidth="8"
                  className={`${(results?.authenticity?.score ?? 0) >= 80 ? 'text-emerald-500' : 'text-amber-500'}`}
                  fill="none"
                  strokeDasharray={377}
                  strokeDashoffset={377 - (377 * (results?.authenticity?.score ?? 0)) / 100}
                  style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center text-3xl font-bold text-white">
                {results?.authenticity?.score ?? 0}%
              </div>
            </div>
            <p className="mt-4 text-white/50 text-sm text-center">Based on behavioral patterns and content analysis</p>
          </div>
        </div>

        {/* Sentiment Card */}
        <div className="glass-card p-6 rounded-2xl group hover:bg-white/5 transition-all duration-500">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-xl bg-purple-500/20 text-purple-400">
              <ChatBubbleLeftRightIcon className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold text-white">Sentiment</h3>
          </div>

          <div className="space-y-6">
            {[
              { label: 'Positive', val: results?.sentiment?.positive ?? 0, color: 'bg-emerald-500' },
              { label: 'Neutral', val: results?.sentiment?.neutral ?? 0, color: 'bg-gray-500' },
              { label: 'Negative', val: results?.sentiment?.negative ?? 0, color: 'bg-rose-500' },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-white/80">{item.label}</span>
                  <span className="text-white/40">{item.val}%</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${item.color} transition-all duration-1000 ease-out`}
                    style={{ width: `${item.val}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Deep Content Analysis */}
      <div className="glass-panel p-8 rounded-2xl">
        <h3 className="text-2xl font-bold text-white mb-8 border-b border-white/5 pb-4">Content Intelligence</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4 text-primary-300">
              <HashtagIcon className="w-5 h-5" />
              <h4 className="font-semibold uppercase tracking-wider text-xs">Top Topics</h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {results?.content_analysis?.topics?.map((topic, i) => (
                <span key={i} className="px-4 py-2 rounded-lg bg-primary-500/10 text-primary-200 border border-primary-500/20 text-sm hover:bg-primary-500/20 transition-colors cursor-default">
                  {topic}
                </span>
              ))}
              {!results?.content_analysis?.topics?.length && <span className="text-white/30 text-sm">No topics detected</span>}
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-4 text-secondary-300">
              <LanguageIcon className="w-5 h-5" />
              <h4 className="font-semibold uppercase tracking-wider text-xs">Keywords</h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {results?.content_analysis?.keywords?.map((kw, i) => (
                <span key={i} className="px-3 py-1.5 rounded-lg bg-secondary-500/10 text-secondary-200 border border-secondary-500/20 text-sm hover:bg-secondary-500/20 transition-colors cursor-default">
                  {kw}
                </span>
              ))}
              {!results?.content_analysis?.keywords?.length && <span className="text-white/30 text-sm">No keywords detected</span>}
            </div>
          </div>
        </div>
      </div>

      {/* Raw JSON Fallback */}
      {!results && (
        <div className="glass-panel p-6 rounded-xl">
          <pre className="text-xs text-white/50 overflow-x-auto font-mono">
            {JSON.stringify(task, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default ResultView;
