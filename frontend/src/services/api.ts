// API Service for ProfileScope Frontend
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  Analysis, 
  AnalysisRequest, 
  ApiResponse, 
  DashboardStats 
} from '@/types';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || '/api';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(email: string, password: string): Promise<ApiResponse<{ user: User; token: string }>> {
    try {
      const response = await this.api.post('/auth/login', { email, password });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async register(userData: {
    email: string;
    password: string;
    username?: string;
    firstName?: string;
    lastName?: string;
  }): Promise<ApiResponse<{ user: User; token: string }>> {
    try {
      const response = await this.api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    try {
      const response = await this.api.get('/auth/me');
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Analysis Management
  async createAnalysis(request: AnalysisRequest): Promise<ApiResponse<Analysis>> {
    try {
      const response = await this.api.post('/analysis', request);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getAnalysis(analysisId: number): Promise<ApiResponse<Analysis>> {
    try {
      const response = await this.api.get(`/analysis/${analysisId}`);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getUserAnalyses(page = 1, limit = 10): Promise<ApiResponse<{
    analyses: Analysis[];
    total: number;
    page: number;
    pages: number;
  }>> {
    try {
      const response = await this.api.get('/analysis', {
        params: { page, limit }
      });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async deleteAnalysis(analysisId: number): Promise<ApiResponse<void>> {
    try {
      await this.api.delete(`/analysis/${analysisId}`);
      return { success: true };
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Dashboard & Statistics
  async getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
    try {
      const response = await this.api.get('/dashboard/stats');
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Real-time Analysis Status
  async getAnalysisStatus(analysisId: number): Promise<ApiResponse<{
    status: string;
    progress: number;
    message?: string;
  }>> {
    try {
      const response = await this.api.get(`/analysis/${analysisId}/status`);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Profile Search/Validation
  async validateProfile(platform: string, profileId: string): Promise<ApiResponse<{
    exists: boolean;
    displayName?: string;
    verified?: boolean;
  }>> {
    try {
      const response = await this.api.get('/profile/validate', {
        params: { platform, profile_id: profileId }
      });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Export & Reports
  async exportAnalysis(analysisId: number, format: 'json' | 'pdf' | 'csv'): Promise<Blob> {
    try {
      const response = await this.api.get(`/analysis/${analysisId}/export`, {
        params: { format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // WebSocket connection for real-time updates
  connectToAnalysisUpdates(analysisId: number, onUpdate: (data: any) => void): WebSocket {
    const wsUrl = this.baseURL.replace('http', 'ws') + `/ws/analysis/${analysisId}`;
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onUpdate(data);
    };
    
    return ws;
  }

  // Error handling
  private handleError(error: any): ApiResponse<never> {
    console.error('API Error:', error);
    
    const message = error.response?.data?.message || 
                   error.response?.data?.error || 
                   error.message || 
                   'An unexpected error occurred';
                   
    return {
      success: false,
      error: message
    };
  }

  // Utility methods
  setAuthToken(token: string): void {
    localStorage.setItem('auth_token', token);
  }

  removeAuthToken(): void {
    localStorage.removeItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }
}

// Create and export singleton instance
export const apiService = new ApiService();
export default apiService;