export interface User {
    id: number;
    email: string;
    full_name: string;
    institution?: string;
    is_admin: boolean;
}

export interface LoginCredentials {
    email: string;
    password?: string;
}

export interface RegisterData {
    email: string;
    password?: string;
    full_name: string;
    institution?: string;
}
export interface WirelessFile {
    id?: number; 
    filename: string;
    file_path: string;
    file_size: number;
    raw_upload_time?: string;
    dataset_name?: string;
    
    // The new Medallion properties:
    processing_status?: string;
    sensor_type?: string;
}
export interface WirelessFile {
    id?: number;
    filename: string;
    file_path: string;
    file_size: number;
    raw_upload_time?: string;
    dataset_name?: string;
    processing_status?: string;
    sensor_type?: string;
    uploader_name?: string; // 🚨 Add this!
}
export interface AuthResponse {
    success: boolean;
    user: User;
    error?: string;
}

// ── NEW: Modality and Tab Types ──
export type Modality = 'wifi' | 'radar' | 'lidar' | 'unspecified';
export type Tab = 'mydata' | 'wifi' | 'radar' | 'lidar' | 'jupyter' | 'gold';

export interface WirelessFile {
    id?: number;
    filename: string;
    file_path: string;
    file_size: number;
    file_extension: string;
    dataset_name?: string;
    modality?: Modality; 
    raw_upload_time?: string;
    upload_timezone?: string;
    researcher_name?: string;
}

export interface FilesResponse {
    success: boolean;
    files: WirelessFile[]; 
    error?: string;
    my_files?: WirelessFile[];  
    lab_files?: WirelessFile[];
}

export interface AnalysisResponse {
    success: boolean;
    metadata?: any;
    error?: string;
}

export interface ApiResponse {
    success: boolean;
    message?: string;
    error?: string;
}