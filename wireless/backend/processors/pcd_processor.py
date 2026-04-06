import os
import tempfile
import pandas as pd
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

class PCDProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        
        # Smart Pathing: Detect if it's already a local file or an Azure blob path
        if os.path.exists(self.file_path):
            self.local_temp_path = self.file_path
            self.needs_cleanup = False # The app.py Janitor handles cleanup
        else:
            self.local_temp_path = None
            self.needs_cleanup = True  # We will download it, so we must clean it up

    def _download_from_azure(self):
        """Pulls the file from Azure to a temporary location for metadata extraction."""
        if not self.local_temp_path:
            bsc = BlobServiceClient.from_connection_string(os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
            container_name = os.getenv('BRONZE_CONTAINER_NAME', 'bronze-layer')
            blob_client = bsc.get_blob_client(container=container_name, blob=self.file_path)
            
            temp_dir = tempfile.gettempdir()
            self.local_temp_path = os.path.join(temp_dir, self.filename)
            
            print(f"📥 Downloading {self.filename} from Azure for Lidar processing...")
            with open(self.local_temp_path, "wb") as f:
                f.write(blob_client.download_blob().readall())

    def __del__(self):
        """Cleans up the temp file to save your Mac's hard drive space."""
        if getattr(self, 'needs_cleanup', False) and self.local_temp_path and os.path.exists(self.local_temp_path):
            try:
                os.remove(self.local_temp_path)
                print(f"🧹 Cleaned up temp file: {self.local_temp_path}")
            except Exception:
                pass

    def get_metadata(self):
        try:
            if not self.local_temp_path:
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

    def read_file(self):
        """
        Extracts the actual 3D point arrays into a Pandas DataFrame.
        Used by the Silver Layer ETL if you want to convert PCD to Parquet.
        """
        if not self.local_temp_path:
            self._download_from_azure()
            
        header_lines = 0
        data_format = 'ascii'
        fields = []
        
        # 1. First pass: find out where the header ends and what the fields are
        with open(self.local_temp_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                header_lines += 1
                line = line.strip()
                if line.startswith('FIELDS'):
                    fields = line.split()[1:]
                elif line.startswith('DATA'):
                    if len(line.split()) > 1:
                        data_format = line.split()[1].lower()
                    break
        
        # 2. Extract the data based on the format
        if data_format == 'ascii':
            # Pandas is highly optimized for reading massive ASCII space-separated files
            print(f"🔄 Parsing ASCII PCD data into DataFrame...")
            df = pd.read_csv(self.local_temp_path, sep=r'\s+', skiprows=header_lines, names=fields, engine='c')
            return df
        else:
            # Binary PCD files require complex struct unpacking (or libraries like open3d)
            raise NotImplementedError("Binary PCD parsing is complex. For production, consider using the 'open3d' Python library to read binary .pcd files.")


# --- HELPER FUNCTION FOR APP.PY ROUTING ---
def process_pcd(file_path):
    """Wrapper function so app.py can call this easily."""
    processor = PCDProcessor(file_path)
    return processor.get_metadata()