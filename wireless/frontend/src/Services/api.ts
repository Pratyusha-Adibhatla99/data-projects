/**
 * API Service Layer
 * All backend communication goes through here
 */

import axios from 'axios';
import type { AxiosInstance } from 'axios'; 
import type {
  LoginCredentials,
  RegisterData,
  AuthResponse,
  FilesResponse,
  AnalysisResponse,
  ApiResponse,
  User,
} from '../Types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      // FIX 2: Vite uses import.meta.env instead of process.env
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5001', 
      withCredentials: true, // Important for Flask sessions
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Unauthorized - redirect to login
          window.location.href = '/';
        }
        return Promise.reject(error);
      }
    );
  }

  // ==========================================
  // AUTHENTICATION
  // ==========================================

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const { data } = await this.client.post<AuthResponse>('/api/login', credentials);
    return data;
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    const { data } = await this.client.post<AuthResponse>('/api/register', userData);
    return data;
  }

  async logout(): Promise<void> {
    await this.client.post('/api/logout');
  }

  async getCurrentUser(): Promise<AuthResponse> {
    const { data } = await this.client.get<AuthResponse>('/api/current-user');
    return data;
  }

  // ==========================================
  // FILE OPERATIONS
  // ==========================================

  async uploadFiles(files: FileList, datasetName: string, modality: string): Promise<ApiResponse> {
    const formData = new FormData();
    formData.append('dataset_name', datasetName);
    formData.append('modality', modality); 
    
    Array.from(files).forEach((file) => {
      formData.append('file', file);
    });

    const { data } = await this.client.post<ApiResponse>('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  }
  async getMyFiles(): Promise<FilesResponse> {
    const { data } = await this.client.get<FilesResponse>('/api/files');
    return data;
  }

  async getHubFiles(modality: 'wifi' | 'radar' | 'lidar'): Promise<FilesResponse> {
    const { data } = await this.client.get<FilesResponse>(`/api/silver/hub/${modality}`);
    return data;
  }

  // ==========================================
  // ANALYSIS
  // ==========================================

  async analyzeFile(filePath: string): Promise<AnalysisResponse> {
    const encodedPath = encodeURIComponent(filePath);
    const { data } = await this.client.get<AnalysisResponse>(`/api/analyze?path=${encodedPath}`);
    return data;
  }
  async getAllUsers(): Promise<{ success: boolean; users: User[]; error?: string }> {
    const { data } = await this.client.get('/api/users');
    return data;
  }
  // ==========================================
  // JUPYTER & MEDALLION
  // ==========================================

  async launchNotebook(): Promise<{ success: boolean; url?: string; error?: string }> {
    const { data } = await this.client.post('/api/notebook/launch');
    return data;
  }

  async getBronzeFiles(): Promise<FilesResponse> {
    const { data } = await this.client.get<FilesResponse>('/api/bronze/files');
    return data;
  }

  async getSilverFiles(): Promise<{ success: boolean; files: any[] }> {
    const { data } = await this.client.get('/api/silver/files');
    return data;
  }

  async triggerSilverTransformation(bronzeFileId: number): Promise<ApiResponse> {
    const { data } = await this.client.post('/api/silver/transform', { bronze_file_id: bronzeFileId });
    return data;
  }
}

export const api = new ApiService();
export default api;