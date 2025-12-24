// Dashboard Component for ProfileScope
// Shows recent tasks and platform breakdown
import React, { useEffect, useState } from 'react';
import {
  ChartBarIcon,
  CheckCircleIcon,
  ClockIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { apiService } from '@/services/api';
import AnalysisForm from '@/components/AnalysisForm';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

type Task = {
  id: number;
  platform: string;
  profile_id?: string;
  profileId?: string;
  status: string;
  progress?: number;
  message?: string;
  created_at?: string;
  createdAt?: string;
};

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [showNewAnalysis, setShowNewAnalysis] = useState(false);

  const [tasks, setTasks] = useState<Task[]>([]);
  const [platformDist, setPlatformDist] = useState<Array<{ platform: string; count: number }>>([]);
  const [completionRate, setCompletionRate] = useState<{ total: number; completed: number; failed: number; completion_rate: number } | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const [tasksResp, distResp, rateResp] = await Promise.all([
        apiService.listTasks({ limit: 10, offset: 0 }),
        apiService.getPlatformDistribution(),
        apiService.getCompletionRate(),
      ]);

      if (tasksResp.success && tasksResp.data?.tasks) {
        setTasks(tasksResp.data.tasks);
      }
      if (distResp.success && Array.isArray(distResp.data)) {
        setPlatformDist(distResp.data);
      }
      if (rateResp.success && rateResp.data) {
        setCompletionRate(rateResp.data);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const pieData = platformDist.map((p) => ({ name: p.platform, value: p.count }));

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6 md:flex md:items-center md:justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
                Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Recent analysis tasks and platform distribution.
              </p>
            </div>
            <div className="mt-4 flex md:mt-0 md:ml-4">
              <button
                onClick={() => setShowNewAnalysis(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                New Analysis
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <ChartBarIcon className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <div className="text-sm text-gray-500">Total Tasks</div>
                <div className="text-2xl font-semibold text-gray-900">{completionRate?.total ?? tasks.length}</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <CheckCircleIcon className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <div className="text-sm text-gray-500">Completed</div>
                <div className="text-2xl font-semibold text-gray-900">{completionRate?.completed ?? 0}</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <ClockIcon className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <div className="text-sm text-gray-500">Completion Rate</div>
                <div className="text-2xl font-semibold text-gray-900">{(completionRate?.completion_rate ?? 0).toFixed(1)}%</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <div className="text-sm text-gray-500">Failed</div>
                <div className="text-2xl font-semibold text-gray-900">{completionRate?.failed ?? 0}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Platform Breakdown</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) => `${name} ${Math.round((percent ?? 0) * 100)}%`}
                >
                  {pieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Tasks</h3>
            </div>
            <div className="divide-y divide-gray-200">
              {tasks.length ? (
                tasks.map((t) => (
                  <div key={t.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {t.platform} / {(t.profile_id ?? t.profileId) ?? ''}
                        </div>
                        <div className="text-sm text-gray-500">{t.status}{t.progress != null ? ` • ${t.progress}%` : ''}{t.message ? ` • ${t.message}` : ''}</div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="px-6 py-8 text-center">
                  <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks yet</h3>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {showNewAnalysis && (
        <AnalysisForm
          onAnalysisCreated={() => {
            setShowNewAnalysis(false);
            load();
          }}
          onClose={() => setShowNewAnalysis(false)}
        />
      )}
    </div>
  );
};

export default Dashboard;
