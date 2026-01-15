// Analysis Form Component for ProfileScope
import React, { useState } from 'react';
import {
  MagnifyingGlassIcon,
  PhotoIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { AnalysisRequest } from '@/types';
import { apiService } from '@/services/api';

interface AnalysisFormProps {
  onAnalysisCreated: (analysisId: number) => void;
  onClose: () => void;
}

const AnalysisForm: React.FC<AnalysisFormProps> = ({ onAnalysisCreated, onClose }) => {
  const [formData, setFormData] = useState<AnalysisRequest>({
    platform: 'twitter',
    profileId: '',
    includeImages: true,
    includePosts: true,
    postCount: 20
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const platforms = [
    { id: 'twitter', name: 'Twitter/X', icon: '🐦' },
    { id: 'instagram', name: 'Instagram', icon: '📸' },
    { id: 'linkedin', name: 'LinkedIn', icon: '💼' },
    { id: 'tiktok', name: 'TikTok', icon: '🎵' },
    { id: 'facebook', name: 'Facebook', icon: '👥' }
  ];

  const handleProfileIdChange = (value: string) => {
    setFormData(prev => ({ ...prev, profileId: value }));
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await apiService.createAnalysis(formData);
      if (response.success && (response.data as any)?.task?.id) {
        onAnalysisCreated((response.data as any).task.id);
        onClose();
      } else {
        setError(response.error || 'Failed to create analysis');
      }
    } catch {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Glass Modal */}
      <div className="relative w-full max-w-2xl transform overflow-hidden glass-panel rounded-2xl p-8 transition-all animate-fade-in-up">
        <div className="absolute top-0 right-0 pt-4 pr-4">
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-white/50 hover:text-white hover:bg-white/10 transition-colors"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="mb-6">
          <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60 font-display">
            Start New Analysis
          </h3>
          <p className="mt-2 text-sm text-white/50">
            Configure target profile and analysis parameters.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Platform Selection */}
          <div>
            <label className="block text-sm font-medium text-white/90 mb-3">
              Target Platform
            </label>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {platforms.map((platform) => (
                <button
                  key={platform.id}
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, platform: platform.id as any }))}
                  className={`
                    flex items-center justify-center p-4 rounded-xl border transition-all duration-300
                    ${formData.platform === platform.id
                      ? 'bg-primary-500/20 border-primary-500/50 shadow-[0_0_15px_rgba(99,102,241,0.2)]'
                      : 'bg-white/5 border-white/5 hover:bg-white/10 hover:border-white/20'
                    }
                  `}
                >
                  <span className="text-xl mr-2">{platform.icon}</span>
                  <span className={`text-sm font-medium ${formData.platform === platform.id ? 'text-white' : 'text-white/70'}`}>
                    {platform.name}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Profile ID */}
          <div>
            <label className="block text-sm font-medium text-white/90 mb-2">
              Profile Username (without @)
            </label>
            <div className="relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg blur opacity-30 group-hover:opacity-100 transition duration-1000"></div>
              <input
                type="text"
                value={formData.profileId}
                onChange={(e) => handleProfileIdChange(e.target.value)}
                placeholder="e.g. elonmusk"
                className="relative block w-full bg-black/50 border border-white/10 rounded-lg py-3 px-4 text-white placeholder-white/30 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all font-mono"
                required
              />
            </div>
          </div>

          {/* Analysis Options */}
          <div className="space-y-4 bg-white/5 rounded-xl p-4 border border-white/5">
            <h4 className="text-sm font-medium text-white/80">Analysis Depth</h4>

            <div className="flex items-center justify-between">
              <label htmlFor="include-posts" className="flex items-center cursor-pointer">
                <div className={`p-2 rounded-lg mr-3 ${formData.includePosts ? 'bg-primary-500/20 text-primary-300' : 'bg-white/5 text-white/30'}`}>
                  <DocumentTextIcon className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-sm font-medium text-white">Analyze Posts</div>
                  <div className="text-xs text-white/40">Reviews text content & engagement</div>
                </div>
              </label>
              <input
                id="include-posts"
                type="checkbox"
                checked={formData.includePosts}
                onChange={(e) => setFormData(prev => ({ ...prev, includePosts: e.target.checked }))}
                className="h-5 w-5 rounded border-gray-600 text-primary-600 focus:ring-primary-500 bg-white/10"
              />
            </div>

            {formData.includePosts && (
              <div className="ml-12 pl-2 border-l border-white/10">
                <select
                  value={formData.postCount}
                  onChange={(e) => setFormData(prev => ({ ...prev, postCount: parseInt(e.target.value) }))}
                  className="block w-full bg-black/40 border border-white/10 rounded-lg py-2 px-3 text-sm text-white focus:outline-none focus:border-white/30"
                >
                  <option value={10}>Analyze last 10 posts</option>
                  <option value={20}>Analyze last 20 posts</option>
                  <option value={50}>Analyze last 50 posts</option>
                  <option value={100}>Analyze last 100 posts</option>
                </select>
              </div>
            )}

            <div className="flex items-center justify-between pt-2">
              <label htmlFor="include-images" className="flex items-center cursor-pointer">
                <div className={`p-2 rounded-lg mr-3 ${formData.includeImages ? 'bg-secondary-500/20 text-secondary-300' : 'bg-white/5 text-white/30'}`}>
                  <PhotoIcon className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-sm font-medium text-white">Vision Analysis</div>
                  <div className="text-xs text-white/40">Analyze profile pictures & media</div>
                </div>
              </label>
              <input
                id="include-images"
                type="checkbox"
                checked={formData.includeImages}
                onChange={(e) => setFormData(prev => ({ ...prev, includeImages: e.target.checked }))}
                className="h-5 w-5 rounded border-gray-600 text-secondary-600 focus:ring-secondary-500 bg-white/10"
              />
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="rounded-lg bg-rose-500/10 border border-rose-500/20 p-4 flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-rose-400 mr-3" />
              <p className="text-sm text-rose-300">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2.5 rounded-xl text-sm font-medium text-white/70 hover:text-white hover:bg-white/5 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !formData.profileId.trim()}
              className="glass-button flex items-center bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              {loading && (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white mr-2"></div>
              )}
              {!loading && <MagnifyingGlassIcon className="h-4 w-4 mr-2 group-hover:scale-110 transition-transform" />}
              Start Analysis
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AnalysisForm;