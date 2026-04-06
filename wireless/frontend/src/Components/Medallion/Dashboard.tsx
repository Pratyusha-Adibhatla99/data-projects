import React, { useEffect, useState } from 'react';
import type { User, WirelessFile } from '../../Types'; 
import { useFiles } from '../../hooks/useFiles';
import UploadZone from '../Upload/UploadZone';
import MetadataModal from './MetadataModal';

interface DashboardProps {
    user: User;
    setUser: React.Dispatch<React.SetStateAction<User | null>>;
}

// 🎨 Official UC San Diego Brand Colors
const UCSD = {
    Navy: '#182B49',
    Gold: '#C69214',
    Yellow: '#FFCD00',
    Teal: '#00C6D7',
    LightGray: '#F3F4F6',
    DarkGray: '#374151'
};

export default function Dashboard({ user, setUser }: DashboardProps) {
    // 1 & 2: The New Hook Integration
    const { groupedFiles, loading, loadFiles, currentTab } = useFiles();
    const [isLaunchingJupyter, setIsLaunchingJupyter] = useState(false);
    
    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedMetadata, setSelectedMetadata] = useState<any>(null);
    const [selectedFilename, setSelectedFilename] = useState<string>("");
    const [analyzingFileId, setAnalyzingFileId] = useState<string | number | null>(null);

    // Initial Load
    useEffect(() => { 
        loadFiles('mydata'); 
    }, [loadFiles]);

    const handleLaunchJupyter = () => {
        setIsLaunchingJupyter(true);
        setTimeout(() => {
            window.open('http://localhost:8888/lab', '_blank');
            setIsLaunchingJupyter(false);
        }, 1000);
    };

    // --- RENDER ---
    return (
        <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '40px 20px', fontFamily: 'system-ui, sans-serif' }}>
            
            {/* Header Section */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', background: UCSD.Navy, padding: '24px', borderRadius: '12px', color: 'white', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ color: UCSD.Yellow }}>📡</span> WCSNG @ UC San Diego
                    </h1>
                    <p style={{ margin: '4px 0 0 0', color: '#cbd5e1', fontSize: '14px' }}>
                        Logged in as <strong>{user.full_name}</strong> | Secure Medallion Pipeline Active
                    </p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button onClick={handleLaunchJupyter} style={{ background: UCSD.Yellow, color: UCSD.Navy, border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                        {isLaunchingJupyter ? '⏳ Starting...' : '🚀 Launch Jupyter'}
                    </button>
                    <button onClick={() => setUser(null)} style={{ background: 'transparent', color: 'white', border: '1px solid white', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer' }}>
                        Logout
                    </button>
                </div>
            </div>

            {/* Upload Zone */}
            <UploadZone onUploadSuccess={() => loadFiles(currentTab)} />

            {/* 3. The New Tabs */}
            <div style={{ display: 'flex', gap: '8px', marginTop: '30px', borderBottom: `2px solid ${UCSD.Navy}` }}>
                <button onClick={() => loadFiles('mydata')} style={tabStyle(currentTab === 'mydata', UCSD.Navy)}>🗂️ My Data (Raw)</button>
                <button onClick={() => loadFiles('wifi')} style={tabStyle(currentTab === 'wifi', UCSD.Gold)}>📡 WiFi (Silver)</button>
                <button onClick={() => loadFiles('radar')} style={tabStyle(currentTab === 'radar', UCSD.Gold)}>🎯 Radar (Silver)</button>
                <button onClick={() => loadFiles('lidar')} style={tabStyle(currentTab === 'lidar', UCSD.Gold)}>🚗 LiDAR (Silver)</button>
                <button onClick={() => loadFiles('gold')} style={tabStyle(currentTab === 'gold', UCSD.Teal)}>✨ ML Ready (Gold)</button>
            </div>

            {/* Workspace Area - Drastically simplified because groupedFiles handles the sorting! */}
            <div style={{ background: 'white', padding: '24px', border: `1px solid #e2e8f0`, borderTop: 'none', minHeight: '400px' }}>
                
                {loading ? ( <p style={emptyStateStyle}>Fetching data from Azure...</p> ) : 
                
                currentTab === 'gold' ? (
                    <div style={emptyStateStyle}>🚧 Feature Engineered Datasets will appear here.</div>
                ) : Object.keys(groupedFiles).length === 0 ? (
                    <p style={emptyStateStyle}>No files found for this category.</p>
                ) : (
                    Object.entries(groupedFiles)
                        // If it's a silver tab, sort by date (newest first). Otherwise, sort alphabetically by folder name.
                        .sort((a, b) => currentTab !== 'mydata' ? new Date(b[0]).getTime() - new Date(a[0]).getTime() : a[0].localeCompare(b[0]))
                        .map(([groupName, fList]) => (
                            <FolderBlock 
                                key={groupName} 
                                title={currentTab === 'mydata' ? `📁 ${groupName}` : `📅 Uploaded on: ${groupName}`} 
                                files={fList} 
                                isSilver={currentTab !== 'mydata'} 
                                setAnalyzingFileId={setAnalyzingFileId} 
                                setIsModalOpen={setIsModalOpen} 
                                setSelectedMetadata={setSelectedMetadata} 
                                setSelectedFilename={setSelectedFilename} 
                            />
                        ))
                )}
            </div>

            <MetadataModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} metadata={selectedMetadata} filename={selectedFilename} />
        </div>
    );
}

// --- HELPER COMPONENTS ---

const tabStyle = (isActive: boolean, activeColor: string) => ({
    padding: '12px 24px',
    background: isActive ? activeColor : '#f8fafc',
    color: isActive ? 'white' : '#64748b',
    border: `1px solid ${isActive ? activeColor : '#e2e8f0'}`,
    borderBottom: 'none',
    borderRadius: '8px 8px 0 0',
    cursor: 'pointer',
    fontWeight: 'bold',
    fontSize: '15px',
    opacity: isActive ? 1 : 0.8
});

const emptyStateStyle = { textAlign: 'center' as const, padding: '40px', color: '#64748b', background: '#f8fafc', borderRadius: '8px' };

// Reusable "Folder" Block for grouping files
const FolderBlock = ({ title, files, isSilver, setAnalyzingFileId, setIsModalOpen, setSelectedMetadata, setSelectedFilename }: any) => (
    <div style={{ marginBottom: '24px', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden' }}>
        <div style={{ background: UCSD.LightGray, padding: '12px 16px', fontWeight: 'bold', color: UCSD.Navy, borderBottom: '1px solid #e2e8f0' }}>
            {title} <span style={{ marginLeft: '8px', fontSize: '12px', background: '#e2e8f0', padding: '2px 8px', borderRadius: '12px', color: '#64748b' }}>{files.length} items</span>
        </div>
        <div>
            {files.map((file: any) => (
                <div key={file.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', borderBottom: '1px solid #f1f5f9', background: 'white' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ fontSize: '20px' }}>{isSilver ? '📊' : '📄'}</span>
                        <div>
                            <div style={{ color: UCSD.DarkGray, fontWeight: '500', fontSize: '14px' }}>
                                {isSilver ? file.filename.replace(/\.[^/.]+$/, "") + '.parquet' : file.filename}
                            </div>
                            <div style={{ color: '#94a3b8', fontSize: '12px' }}>
                                {(file.file_size / (1024 * 1024)).toFixed(2)} MB
                            </div>
                            {/* Shows the uploader's name on Lab/Silver data */}
                            {isSilver && file.uploader_name && (
                                <div style={{ color: '#0ea5e9', fontSize: '12px', marginTop: '2px', fontWeight: 'bold' }}>
                                    Uploaded by: {file.uploader_name}
                                </div>
                            )}
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button onClick={() => alert('Connect to Flask API for Analyze')} style={{ cursor: 'pointer', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '4px', padding: '6px 12px' }}>🔍 Analyze</button>
                        <button onClick={() => alert('Connect to Flask API for Download')} style={{ cursor: 'pointer', background: '#eff6ff', color: UCSD.Navy, border: `1px solid ${UCSD.Navy}`, borderRadius: '4px', padding: '6px 12px', fontWeight: 'bold' }}>⬇️ Download</button>
                    </div>
                </div>
            ))}
        </div>
    </div>
);