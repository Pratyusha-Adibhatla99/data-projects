import os
import tempfile
import numpy as np
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

class WirelessDataProcessor:
    def __init__(self, blob_path):
        self.blob_path = blob_path
        self.filename = os.path.basename(blob_path)
        self.local_temp_path = None

    def _download_from_azure(self):
        """Pulls the file from Azure to a temporary location for analysis."""
        if not self.local_temp_path:
            bsc = BlobServiceClient.from_connection_string(os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
            container_name = os.getenv('BRONZE_CONTAINER_NAME', 'bronze-layer')
            blob_client = bsc.get_blob_client(container=container_name, blob=self.blob_path)
            
            temp_dir = tempfile.gettempdir()
            self.local_temp_path = os.path.join(temp_dir, self.filename)
            
            print(f"📥 Downloading {self.filename} from Azure for metadata extraction...")
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

        variables = {}
        skip_keys = {'__header__', '__version__', '__globals__'}

        # ── 1. Try Standard v5 MAT files (scipy) ──
        try:
            import scipy.io as sio
            mat_data = sio.loadmat(self.local_temp_path)
            
            for key, value in mat_data.items():
                if key in skip_keys: continue
                
                # key is the Variable/Column Name
                if isinstance(value, np.ndarray):
                    variables[key] = {
                        'shape': list(value.shape),
                        'dtype': str(value.dtype)
                    }
                else:
                    variables[key] = {
                        'shape': [], 
                        'dtype': type(value).__name__
                    }

        # ── 2. Try v7.3 HDF5 MAT files (h5py) ──
        except Exception:
            try:
                import h5py
                with h5py.File(self.local_temp_path, 'r') as f:
                    for key in f.keys():
                        if key in skip_keys: continue
                        dataset = f[key]
                        
                        # key is the Variable/Column Name
                        if isinstance(dataset, h5py.Dataset):
                            variables[key] = {
                                'shape': list(dataset.shape),
                                'dtype': str(dataset.dtype)
                            }
                        else:
                            variables[key] = {
                                'shape': [], 
                                'dtype': 'HDF5 Group'
                            }
            except ImportError:
                return {'success': False, 'error': 'h5py not installed. Run: pip install h5py'}

        # ── Return Final Schema Dictionary ──
        file_size_mb = os.path.getsize(self.local_temp_path) / (1024 * 1024)
        return {
            'success': True,
            'filename': self.filename,
            'file_type': 'MATLAB Workspace',
            'file_size_mb': round(file_size_mb, 4),
            'variables': variables
        }