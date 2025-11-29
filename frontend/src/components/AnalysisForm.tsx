// Analysis Form Component for ProfileScope
import React, { useState } from 'react';
import { 
  MagnifyingGlassIcon, 
  PhotoIcon, 
  DocumentTextIcon,
  ExclamationTriangleIcon 
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
  const [validating, setValidating] = useState(false);
  const [profileExists, setProfileExists] = useState<boolean | null>(null);
  const [error, setError] = useState<string>('');

  const platforms = [
    { id: 'twitter', name: 'Twitter/X', icon: '🐦' },
    { id: 'instagram', name: 'Instagram', icon: '📸' },
    { id: 'linkedin', name: 'LinkedIn', icon: '💼' },
    { id: 'tiktok', name: 'TikTok', icon: '🎵' },
    { id: 'facebook', name: 'Facebook', icon: '👥' }
  ];

  const handleProfileIdChange = async (value: string) => {
    setFormData(prev => ({ ...prev, profileId: value }));
    setProfileExists(null);
    setError('');

    // Validate profile if value is present
    if (value.trim() && formData.platform) {
      setValidating(true);
      try {
        const response = await apiService.validateProfile(formData.platform, value.trim());
        if (response.success && response.data) {
          setProfileExists(response.data.exists);
        }
      } catch (err) {
        console.error('Profile validation error:', err);
      } finally {
        setValidating(false);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await apiService.createAnalysis(formData);
      if (response.success && response.data) {
        onAnalysisCreated(response.data.id);
      } else {
        setError(response.error || 'Failed to create analysis');
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-gray-900">
              Create New Analysis
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <span className="sr-only">Close</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Platform Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Social Media Platform
              </label>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                {platforms.map((platform) => (
                  <button
                    key={platform.id}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, platform: platform.id as any }))}
                    className={`${
                      formData.platform === platform.id
                        ? 'bg-primary-50 border-primary-200 text-primary-900'
                        : 'bg-white border-gray-300 text-gray-900 hover:bg-gray-50'
                    } relative flex items-center justify-center rounded-md border p-4 focus:outline-none focus:ring-2 focus:ring-primary-500`}
                  >
                    <span className="text-lg mr-2">{platform.icon}</span>
                    <span className="text-sm font-medium">{platform.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Profile ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Profile Username (without @)
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={formData.profileId}
                  onChange={(e) => handleProfileIdChange(e.target.value)}
                  placeholder="elonmusk"
                  className={`block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm ${
                    profileExists === false ? 'border-red-300' : 'border-gray-300'
                  }`}
                  required
                />
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  {validating && (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                  )}
                  {!validating && profileExists === true && (
                    <div className="text-green-500">✓</div>
                  )}
                  {!validating && profileExists === false && (
                    <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
                  )}
                </div>
              </div>
              {profileExists === false && (
                <p className="mt-1 text-sm text-red-600">Profile not found on this platform</p>
              )}
            </div>

            {/* Analysis Options */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-gray-900">Analysis Options</h4>
              
              <div className="flex items-center">
                <input
                  id="include-posts"
                  type="checkbox"
                  checked={formData.includePosts}
                  onChange={(e) => setFormData(prev => ({ ...prev, includePosts: e.target.checked }))}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="include-posts" className="ml-3 flex items-center">
                  <DocumentTextIcon className="h-4 w-4 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-700">Analyze recent posts</span>
                </label>
              </div>

              {formData.includePosts && (
                <div className="ml-7">
                  <label className="block text-sm text-gray-700 mb-1">Number of posts to analyze</label>
                  <select
                    value={formData.postCount}
                    onChange={(e) => setFormData(prev => ({ ...prev, postCount: parseInt(e.target.value) }))}
                    className="block w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  >
                    <option value={10}>10 posts</option>
                    <option value={20}>20 posts</option>
                    <option value={50}>50 posts</option>
                    <option value={100}>100 posts</option>
                  </select>
                </div>
              )}

              <div className="flex items-center">
                <input
                  id="include-images"
                  type="checkbox"
                  checked={formData.includeImages}
                  onChange={(e) => setFormData(prev => ({ ...prev, includeImages: e.target.checked }))}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="include-images" className="ml-3 flex items-center">
                  <PhotoIcon className="h-4 w-4 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-700">Analyze profile images</span>
                </label>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="flex">
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
                  <div className="ml-3">
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !formData.profileId.trim() || profileExists === false}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {loading && (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                )}
                <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
                Start Analysis
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AnalysisForm;