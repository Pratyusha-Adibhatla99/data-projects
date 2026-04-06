import React, { useState, useRef } from 'react';
import { useFiles } from '../../hooks/useFiles';
import type { Modality } from '../../Types/index';

interface UploadZoneProps {
    onUploadSuccess: () => void;
}

export default function UploadZone({ onUploadSuccess }: UploadZoneProps) {
    const { uploadFiles, loading:isLoading, error: apiError } = useFiles();
    
    const [datasetName, setDatasetName] = useState('Default_Dataset');
    const [modality, setModality] = useState<Modality>('wifi');
    const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
    const [validationError, setValidationError] = useState<string | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Strict UI Validation Logic
    const validateFiles = (files: FileList, selectedModality: string): boolean => {
        setValidationError(null);
        const validExtensions: Record<string, string[]> = {
            'wifi': ['.mat', '.csv', '.dat'],
            'radar': ['.mat', '.csv', '.dat'],
            'lidar': ['.pcd']
        };

        const allowed = validExtensions[selectedModality];

        for (let i = 0; i < files.length; i++) {
            const fileName = files[i].name.toLowerCase();
            const hasValidExtension = allowed.some(ext => fileName.endsWith(ext));
            
            if (!hasValidExtension) {
                setValidationError(`Invalid file: ${fileName}. ${selectedModality.toUpperCase()} only accepts ${allowed.join(', ')}`);
                return false;
            }
        }
        return true;
    };

    const handleFileSelect = (files: FileList | null) => {
        if (!files || files.length === 0) return;
        if (validateFiles(files, modality)) {
            setSelectedFiles(files);
        } else {
            setSelectedFiles(null);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleModalityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const newModality = e.target.value as Modality;
        setModality(newModality);
        // Re-validate existing files if they change the dropdown
        if (selectedFiles) {
            handleFileSelect(selectedFiles); 
        }
    };

    const handleUpload = async () => {
        if (!selectedFiles) return;
        try {
            await uploadFiles(selectedFiles, datasetName, modality);
            setSelectedFiles(null);
            setDatasetName('Default_Dataset');
            if (fileInputRef.current) fileInputRef.current.value = ''; 
            onUploadSuccess(); 
        } catch (err) {
            console.error("Upload failed", err);
        }
    };

    return (
        <div style={{ marginBottom: '30px', background: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
            <h3 style={{ marginBottom: '16px', color: '#2c3e50' }}>☁️ Upload to Bronze Layer</h3>
            
            <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                <input 
                    type="text" 
                    value={datasetName} 
                    onChange={(e) => setDatasetName(e.target.value)}
                    placeholder="Dataset Folder Name"
                    style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ddd', flexGrow: 1 }}
                />
                
                {/* NEW: Modality Dropdown */}
                <select 
                    value={modality} 
                    onChange={handleModalityChange}
                    style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ddd', backgroundColor: '#f8fafc', fontWeight: 600, color: '#334155' }}
                >
                    <option value="wifi">📶 Wi-Fi Data</option>
                    <option value="radar">📡 Radar Data</option>
                    <option value="lidar">📐 LiDAR Data</option>
                </select>
            </div>

            <div 
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleFileSelect(e.dataTransfer.files); }}
                onClick={() => fileInputRef.current?.click()}
                style={{
                    border: `2px dashed ${isDragging ? '#007bff' : '#cbd5e1'}`,
                    backgroundColor: isDragging ? '#f8faff' : '#f8fafc',
                    padding: '40px 20px',
                    textAlign: 'center',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                }}
            >
                <input type="file" multiple ref={fileInputRef} onChange={(e) => handleFileSelect(e.target.files)} style={{ display: 'none' }} />
                <p style={{ color: '#64748b', margin: 0, fontWeight: 500 }}>
                    {selectedFiles 
                        ? `📁 ${selectedFiles.length} file(s) selected.` 
                        : `Drag & drop ${modality.toUpperCase()} files here`}
                </p>
                <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '8px' }}>
                    Accepted formats: {modality === 'lidar' ? '.pcd' : '.mat, .csv, .dat'}
                </p>
            </div>

            {(validationError || apiError) && (
                <div style={{ padding: '12px', marginTop: '16px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', color: '#ef4444', fontSize: '14px' }}>
                    ❌ {validationError || apiError}
                </div>
            )}

            <button 
                onClick={handleUpload} 
                disabled={!selectedFiles || !!validationError || isLoading}
                className="btn"
                style={{ 
                    marginTop: '16px', 
                    width: '100%', 
                    background: (!selectedFiles || !!validationError || isLoading) ? '#cbd5e1' : '#007bff',
                    cursor: (!selectedFiles || !!validationError || isLoading) ? 'not-allowed' : 'pointer'
                }}
            >
                {isLoading ? 'Uploading to Azure...' : 'Confirm Upload'}
            </button>
        </div>
    );
}