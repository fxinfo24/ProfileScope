// ProfileScope Frontend Types
export interface User {
  id: number;
  email: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  role: 'user' | 'premium' | 'enterprise' | 'admin';
  subscriptionStatus: 'active' | 'inactive' | 'trial' | 'expired';
  apiCallsCount: number;
  apiCallsLimit: number;
  createdAt: string;
}

export interface AnalysisRequest {
  platform: 'twitter' | 'facebook' | 'instagram' | 'linkedin' | 'tiktok';
  profileId: string;
  includeImages?: boolean;
  includePosts?: boolean;
  postCount?: number;
}

export interface Analysis {
  id: number;
  userId: number;
  platform: string;
  profileId: string;
  profileDisplayName?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  message?: string;
  profileData?: ProfileData;
  analysisResults?: AnalysisResults;
  confidenceScore?: number;
  authenticityScore?: number;
  influenceScore?: number;
  processingTime?: number;
  createdAt: string;
  completedAt?: string;
}

export interface ProfileData {
  id: string;
  username: string;
  displayName: string;
  bio: string;
  location?: string;
  followersCount: number;
  followingCount: number;
  postsCount: number;
  verified: boolean;
  createdAt?: string;
  profileImageUrl?: string;
  bannerUrl?: string;
  websiteUrl?: string;
  platform: string;
}

export interface Post {
  id: string;
  text: string;
  createdAt: string;
  likesCount: number;
  retweetsCount?: number;
  repliesCount?: number;
  isRetweet?: boolean;
  media?: MediaItem[];
  hashtags?: string[];
  mentions?: string[];
}

export interface MediaItem {
  type: 'image' | 'video' | 'gif';
  url: string;
  thumbnail?: string;
}

export interface AnalysisResults {
  contentAnalysis: ContentAnalysis;
  authenticityAnalysis: AuthenticityAnalysis;
  predictions: PredictionResults;
  visualAnalysis?: VisualAnalysis;
  summary: string;
}

export interface ContentAnalysis {
  contentThemes: string[];
  writingStyle: {
    tone: string;
    formality: number;
    humorLevel: number;
    emojiUsage: number;
  };
  personalityTraits: {
    openness: number;
    conscientiousness: number;
    extraversion: number;
    agreeableness: number;
    neuroticism: number;
  };
  postingPatterns: {
    frequency: string;
    timing: string;
    consistency: number;
  };
  audienceEngagement: {
    engagementStyle: string;
    communityInteraction: number;
  };
  sentiment: {
    overall: 'positive' | 'negative' | 'neutral';
    positivity: number;
    emotions: Record<string, number>;
  };
  keyInsights: string[];
}

export interface AuthenticityAnalysis {
  overallAuthenticity: {
    score: number;
    confidence: number;
  };
  botLikelihood: number;
  engagementAuthenticity: {
    score: number;
    analysis: string;
  };
  contentAuthenticity: {
    score: number;
    humanLikelihood: number;
  };
  redFlags: string[];
  greenFlags: string[];
  riskAssessment: 'low' | 'medium' | 'high' | 'critical';
}

export interface PredictionResults {
  growthForecast: {
    thirtyDay: number;
    ninetyDay: number;
    oneYear: number;
  };
  contentEvolution: string;
  engagementTrends: string;
  viralPotential: number;
  platformExpansion: string[];
  optimalPosting: {
    times: string[];
    frequency: string;
  };
  successProbability: number;
  actionableInsights: string[];
}

export interface VisualAnalysis {
  imageProperties: {
    dimensions: { width: number; height: number; aspectRatio: number };
    fileSize: number;
    colorStatistics: {
      meanRgb: number[];
      dominantColor: number[];
    };
  };
  faceAnalysis: {
    facesDetected: number;
    primaryFace?: {
      position: { x: number; y: number; width: number; height: number };
      quality: { sharpness: number; brightness: number; contrast: number };
    };
    faceCentered: boolean;
  };
  professionalAssessment: {
    professionalScore: number;
    recommendations: string[];
  };
  authenticityIndicators: {
    authenticityScore: number;
    potentialManipulation: boolean;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface DashboardStats {
  totalAnalyses: number;
  completedAnalyses: number;
  averageAuthenticityScore: number;
  averageInfluenceScore: number;
  platformBreakdown: Record<string, number>;
  recentAnalyses: Analysis[];
}

export interface ChartData {
  name: string;
  value: number;
  color?: string;
}