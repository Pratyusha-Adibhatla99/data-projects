/**
 * Files Hook
 * Manages file operations and state
 */

import { useState, useCallback, useMemo } from 'react';
import { api } from '../Services/api';
import type { WirelessFile, Tab } from '../Types';

export const useFiles = () => {
  const [files, setFiles] = useState<WirelessFile[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentTab, setCurrentTab] = useState<Tab>('mydata');

  // 1. Fetching Logic
  // 1. Fetching Logic
  // 1. Fetching Logic
  const loadFiles = useCallback(async (tab: Tab = 'mydata') => {
    setError(null);
    setIsLoading(true);
    setCurrentTab(tab);

    try {
      // 🚨 Directly hit our new Flask super-route that returns BOTH lists
      // Note: Make sure the port (5001) matches your Flask backend port!
      const response = await fetch('http://localhost:5001/api/files', { 
          credentials: 'include' 
      });
      const data = await response.json();

      if (!data.success) {
          throw new Error(data.error || 'Failed to load files');
      }

      // 🚨 Route the correct Python data array into the React state
      if (tab === 'mydata') {
          // 'mydata' looks at your personal history
          setFiles(data.my_files || []);
      } else if (tab === 'wifi' || tab === 'radar' || tab === 'lidar') {
          // Sensor tabs look at the global lab data and filter for the exact sensor
          const filteredLabData = (data.lab_files || []).filter(
              (f: WirelessFile) => (f.sensor_type || '').toLowerCase() === tab.toLowerCase()
          );
          setFiles(filteredLabData);
      } else {
          // Fallback for 'gold' tab
          setFiles([]);
      }

    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch files';
      setError(errorMessage);
      setFiles([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  
 // 2. The Grouping Logic (Dynamic based on Tab)
  const groupedFiles = useMemo(() => {
    return files.reduce((acc, file) => {
      
      if (currentTab === 'wifi' || currentTab === 'radar' || currentTab === 'lidar') {
          // SILVER LAYER: Group by Date Uploaded
          const dateStr = file.raw_upload_time ? new Date(file.raw_upload_time).toLocaleDateString() : 'Unknown Date';
          if (!acc[dateStr]) acc[dateStr] = [];
          acc[dateStr].push(file);
      } else {
          // BRONZE LAYER (My Data): Group by Dataset Name (Folder)
          const folder = file.dataset_name || 'Uncategorized';
          if (!acc[folder]) acc[folder] = [];
          acc[folder].push(file);
      }
      
      return acc;
    }, {} as Record<string, WirelessFile[]>);
  }, [files, currentTab]); // Making sure currentTab is in the dependency array!

  // 3. Upload Logic
  // 3. Upload Logic
  const uploadFiles = useCallback(async (fileList: FileList, datasetName: string, modality: string) => {
    setError(null);
    setIsLoading(true);

    try {
      const response = await api.uploadFiles(fileList, datasetName, modality);
      if (!response.success) throw new Error(response.error || 'Upload failed');
      
      await loadFiles(currentTab); // Refresh current view
      return response;
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Upload failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [currentTab, loadFiles]);

  return {
    files,
    groupedFiles,         
    loading: isLoading,   
    error,
    fetchMyFiles: () => loadFiles('mydata'), // Aliased for Dashboard compatibility
    loadFiles,
    uploadFiles,
    currentTab,
  };
};