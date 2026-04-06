import React from 'react';

interface MetadataModalProps {
    isOpen: boolean;
    onClose: () => void;
    metadata: any;
    filename: string;
}

export default function MetadataModal({ isOpen, onClose, metadata, filename }: MetadataModalProps) {
    if (!isOpen) return null;

    // 🚨 THE FIX: A recursive function that perfectly unwraps nested dictionaries!
    const renderValue = (value: any): React.ReactNode => {
        // If it's a nested dictionary (like RSSI or ap_aoa)
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            return (
                <div style={{ marginTop: '8px', padding: '12px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    {Object.entries(value).map(([k, v]) => (
                        <div key={k} style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '8px', padding: '4px 0', borderBottom: '1px solid #f1f5f9' }}>
                            <div style={{ fontWeight: 'bold', color: '#475569', fontSize: '13px' }}>{k}</div>
                            <div style={{ color: '#0f172a', fontSize: '13px', fontFamily: 'monospace' }}>
                                {renderValue(v)} {/* Recursion happens here! */}
                            </div>
                        </div>
                    ))}
                </div>
            );
        }
        // If it's an array or a normal value (like "4 x 8754" or "int64")
        return String(value);
    };

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)', zIndex: 1000,
            display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px'
        }}>
            <div style={{
                background: 'white', borderRadius: '12px', width: '100%', maxWidth: '800px',
                maxHeight: '85vh', display: 'flex', flexDirection: 'column',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
            }}>
                {/* Header */}
                <div style={{ padding: '20px', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#f1f5f9', borderRadius: '12px 12px 0 0' }}>
                    <div>
                        <h2 style={{ margin: 0, color: '#0f172a', fontSize: '20px' }}>📊 Dataset Variables & Metadata</h2>
                        <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: '14px', fontWeight: 'bold' }}>{filename}</p>
                    </div>
                    <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: '#64748b' }}>✖</button>
                </div>

                {/* Scrollable Body */}
                <div style={{ padding: '24px', overflowY: 'auto', flex: 1 }}>
                    {metadata && Object.keys(metadata).length > 0 ? (
                        Object.entries(metadata).map(([key, value]) => (
                            <div key={key} style={{ marginBottom: '24px' }}>
                                {/* The Blue Variable Title (e.g., RSSI, ap, ap_aoa) */}
                                <h3 style={{ color: '#3b82f6', borderBottom: '2px solid #e2e8f0', paddingBottom: '8px', marginTop: 0 }}>
                                    {key === '#refs#' ? 'Internal References' : key}
                                </h3>
                                {/* Render the nested data block */}
                                {renderValue(value)}
                            </div>
                        ))
                    ) : (
                        <p style={{ color: '#64748b', textAlign: 'center' }}>No detailed metadata available for this file.</p>
                    )}
                </div>
            </div>
        </div>
    );
}