import os
import tempfile
import numpy as np
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

class WirelessDataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        
        # Smart Pathing:
        # If the file already exists locally (because SilverService downloaded it), use it.
        # Otherwise, assume it's a blob path from the frontend and we need to download it.
        if os.path.exists(self.file_path):
            self.local_temp_path = self.file_path
            self.needs_cleanup = False # The SilverService "Janitor" handles this cleanup
        else:
            self.local_temp_path = None
            self.needs_cleanup = True  # We will download it, so we must clean it up

    def _download_from_azure(self):
        """Pulls the file from Azure to a temporary location for analysis."""
        if not self.local_temp_path:
            bsc = BlobServiceClient.from_connection_string(os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
            container_name = os.getenv('BRONZE_CONTAINER_NAME', 'bronze-layer')
            blob_client = bsc.get_blob_client(container=container_name, blob=self.file_path)
            
            temp_dir = tempfile.gettempdir()
            self.local_temp_path = os.path.join(temp_dir, self.filename)
            
            print(f"📥 Downloading {self.filename} from Azure...")
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
        """Used by the Frontend to get file shapes/types quickly."""
        try:
            if not self.local_temp_path:
                self._download_from_azure()
        except Exception as e:
            return {'success': False, 'error': f"Azure Download Failed: {str(e)}"}

        variables = {}
        skip_keys = {'__header__', '__version__', '__globals__'}

        try:
            import scipy.io as sio
            mat_data = sio.loadmat(self.local_temp_path)
            
            for key, value in mat_data.items():
                if key in skip_keys: continue
                if isinstance(value, np.ndarray):
                    variables[key] = {'shape': list(value.shape), 'dtype': str(value.dtype)}
                else:
                    variables[key] = {'shape': [], 'dtype': type(value).__name__}

        except Exception:
            try:
                import h5py
                with h5py.File(self.local_temp_path, 'r') as f:
                    for key in f.keys():
                        if key in skip_keys: continue
                        dataset = f[key]
                        if isinstance(dataset, h5py.Dataset):
                            variables[key] = {'shape': list(dataset.shape), 'dtype': str(dataset.dtype)}
                        else:
                            variables[key] = {'shape': [], 'dtype': 'HDF5 Group'}
            except ImportError:
                return {'success': False, 'error': 'h5py not installed. Run: pip install h5py'}

        file_size_mb = os.path.getsize(self.local_temp_path) / (1024 * 1024)
        return {
            'success': True,
            'filename': self.filename,
            'file_type': 'MATLAB Workspace',
            'file_size_mb': round(file_size_mb, 4),
            'variables': variables
        }

    def read_file(self):
        """Used by the Silver Layer ETL to extract the ACTUAL data arrays for Parquet conversion."""
        if not self.local_temp_path:
            self._download_from_azure()

        skip_keys = {'__header__', '__version__', '__globals__'}
        
        # 1. Try Standard v5 MAT files
        try:
            import scipy.io as sio
            mat_data = sio.loadmat(self.local_temp_path)
            # Return only the actual data variables, stripping out MATLAB's internal headers
            return {k: v for k, v in mat_data.items() if k not in skip_keys}
            
        # 2. Try v7.3 HDF5 MAT files
        # 2. Try v7.3 HDF5 MAT files
        except Exception:
            import h5py
            data_dict = {}
            
            # Notice we added 'root_file' so we can look up pointers anywhere in the file
            def extract_datasets(group, prefix='', root_file=None):
                """Recursively digs through HDF5 folders and resolves MATLAB pointers."""
                for key in group.keys():
                    if key in skip_keys: continue
                    
                    item = group[key]
                    full_key = f"{prefix}{key}" 
                    
                    if isinstance(item, h5py.Dataset):
                        try:
                            val = item[()]
                            
                            # --- CRITICAL FIX: Resolve MATLAB Object Pointers ---
                            # If the column is full of objects/pointers instead of normal numbers
                            if isinstance(val, np.ndarray) and val.dtype == 'object':
                                resolved_list = []
                                for element in val.flatten():
                                    if isinstance(element, h5py.h5r.Reference) and root_file:
                                        # Follow the pointer to the real data!
                                        deref_obj = root_file[element]
                                        if isinstance(deref_obj, h5py.Dataset):
                                            deref_val = deref_obj[()]
                                            # Convert arrays inside cells to strings so Parquet can save them in one flat column
                                            if isinstance(deref_val, np.ndarray):
                                                resolved_list.append(str(deref_val.flatten().tolist()))
                                            else:
                                                resolved_list.append(str(deref_val))
                                        else:
                                            resolved_list.append("Nested_Group")
                                    else:
                                        # If it's a normal object but not a reference, make it safe text
                                        resolved_list.append(str(element))
                                        
                                # Replace the pointer array with the safe, resolved string array
                                val = np.array(resolved_list)
                            # ----------------------------------------------------

                            data_dict[full_key] = val
                            
                        except Exception as e:
                            print(f"⚠️ Could not read dataset '{full_key}': {e}")
                    
                    elif isinstance(item, h5py.Group):
                        extract_datasets(item, prefix=f"{full_key}_", root_file=root_file)
            
            # Open the file and start extraction, passing 'f' as the root_file
            with h5py.File(self.local_temp_path, 'r') as f:
                extract_datasets(f, root_file=f)
                
            return data_dict
