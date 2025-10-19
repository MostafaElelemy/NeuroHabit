/**
 * API service layer for backend communication.
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_premium: boolean;
  pet_level: number;
  pet_experience: number;
  pet_happiness: number;
  created_at: string;
}

export interface Habit {
  id: number;
  user_id: number;
  title: string;
  description?: string;
  category?: string;
  frequency: string;
  target_count: number;
  color: string;
  icon: string;
  is_active: boolean;
  current_streak: number;
  longest_streak: number;
  difficulty_rating: number;
  importance_rating: number;
  created_at: string;
  updated_at?: string;
}

export interface HabitEvent {
  id: number;
  habit_id: number;
  completed_at: string;
  notes?: string;
  mood?: number;
  energy_level?: number;
  time_of_day?: string;
  day_of_week?: number;
}

export interface HabitStats {
  total_habits: number;
  active_habits: number;
  total_completions: number;
  average_streak: number;
  completion_rate: number;
}

export interface DashboardData {
  user: User;
  habits: Habit[];
  stats: HabitStats;
  recent_events: HabitEvent[];
}

export interface PredictionResponse {
  risk_score: number;
  success_probability: number;
  feature_importance: Array<{
    feature: string;
    importance: number;
  }>;
  recommendation: string;
}

// Auth API
export const authAPI = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/token', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  register: async (email: string, password: string, fullName?: string) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  googleAuth: async () => {
    const response = await api.get('/auth/google');
    return response.data;
  },
};

// User API
export const userAPI = {
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/users/me');
    return response.data;
  },

  updateUser: async (data: Partial<User>): Promise<User> => {
    const response = await api.put('/users/me', data);
    return response.data;
  },
};

// Habit API
export const habitAPI = {
  getHabits: async (): Promise<Habit[]> => {
    const response = await api.get('/habits');
    return response.data;
  },

  getHabit: async (id: number): Promise<Habit> => {
    const response = await api.get(`/habits/${id}`);
    return response.data;
  },

  createHabit: async (data: Partial<Habit>): Promise<Habit> => {
    const response = await api.post('/habits', data);
    return response.data;
  },

  updateHabit: async (id: number, data: Partial<Habit>): Promise<Habit> => {
    const response = await api.put(`/habits/${id}`, data);
    return response.data;
  },

  deleteHabit: async (id: number): Promise<void> => {
    await api.delete(`/habits/${id}`);
  },

  getHabitEvents: async (habitId: number): Promise<HabitEvent[]> => {
    const response = await api.get(`/habits/${habitId}/events`);
    return response.data;
  },

  createHabitEvent: async (
    habitId: number,
    data: Partial<HabitEvent>
  ): Promise<HabitEvent> => {
    const response = await api.post(`/habits/${habitId}/events`, data);
    return response.data;
  },
};

// Dashboard API
export const dashboardAPI = {
  getDashboard: async (): Promise<DashboardData> => {
    const response = await api.get('/dashboard');
    return response.data;
  },
};

// ML Prediction API
export const predictionAPI = {
  predictHabitSuccess: async (
    habitId: number,
    context?: Record<string, any>
  ): Promise<PredictionResponse> => {
    const response = await api.post('/predict', {
      habit_id: habitId,
      context,
    });
    return response.data;
  },
};

export default api;
