import os
import tempfile
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

class PCDProcessor:
    def __init__(self, blob_path):
        self.blob_path = blob_path
        self.filename = os.path.basename(blob_path)
        self.local_temp_path = None

    def _download_from_azure(self):
        """Pulls the file from Azure to a temporary location for metadata extraction."""
        if not self.local_temp_path:
            bsc = BlobServiceClient.from_connection_string(os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
            container_name = os.getenv('BRONZE_CONTAINER_NAME', 'bronze-layer')
            blob_client = bsc.get_blob_client(container=container_name, blob=self.blob_path)
            
            temp_dir = tempfile.gettempdir()
            self.local_temp_path = os.path.join(temp_dir, self.filename)
            
            print(f"📥 Downloading {self.filename} from Azure for Lidar metadata extraction...")
            with open(self.local_temp_path, "wb") as f:
                f.write(blob_client.download_blob().readall())

    def __del__(self):
        """Cleans up the temp file to save your Mac's hard drive space."""
        if self.local_temp_path and os.path.exists(self.local_temp_path):
            os.remove(self.local_temp_path)
            print(f"🧹 Cleaned up temp file: {self.local_temp_path}")

    def get_metadata(self):
        try:
            self._download_from_azure()
        except Exception as e:
            return {'success': False, 'error': f"Azure Download Failed: {str(e)}"}

        header_data = {}
        variables = {}
        
        # ── Fast Header Parsing (Immune to Out-Of-Memory Crashes) ──
        try:
            with open(self.local_temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    
                    parts = line.split()
                    key = parts[0].upper()
                    
                    if key in ['VERSION', 'WIDTH', 'HEIGHT', 'POINTS', 'DATA']:
                        header_data[key] = parts[1] if len(parts) > 1 else ""
                    elif key in ['FIELDS', 'SIZE', 'TYPE', 'COUNT']:
                        header_data[key] = parts[1:]
                        
                    if key == 'DATA':
                        # Stop reading immediately! Do not load the millions of 3D points into memory.
                        break 
            
            # ── Construct the variables schema (like columns in CSV) ──
            fields = header_data.get('FIELDS', [])
            sizes = header_data.get('SIZE', [])
            types = header_data.get('TYPE', [])
            num_points = int(header_data.get('POINTS', 0))
            
            # Map PCD types (I=Int, U=UInt, F=Float) to readable strings
            type_map = {'I': 'Integer', 'U': 'Unsigned Integer', 'F': 'Float'}
            
            for i, field in enumerate(fields):
                # Fallbacks in case the header is slightly malformed
                f_size = sizes[i] if i < len(sizes) else "Unknown"
                f_type = types[i] if i < len(types) else "Unknown"
                readable_type = f"{type_map.get(f_type, f_type)} ({f_size} bytes)"
                
                variables[field] = {
                    'shape': [num_points],
                    'dtype': readable_type
                }
                
        except Exception as e:
            return {'success': False, 'error': f"Failed to parse PCD header: {str(e)}"}

        file_size_mb = os.path.getsize(self.local_temp_path) / (1024 * 1024)
        
        return {
            'success': True,
            'filename': self.filename,
            'file_type': f"Point Cloud Data (PCD v{header_data.get('VERSION', 'Unknown')})",
            'file_size_mb': round(file_size_mb, 4),
            'variables': variables
        }