import pandas as pd
import numpy as np
import os
import tempfile
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

class CSVProcessor:
    def __init__(self, blob_path):
        self.blob_path = blob_path # This is now the Azure path (e.g., pratyusha/000004.csv)
        self.filename = os.path.basename(blob_path)
        self.df = None
        self.local_temp_path = None

    def _download_from_azure(self):
        """Pulls the file from Azure to a temporary location for Pandas to read."""
        if not self.local_temp_path:
            bsc = BlobServiceClient.from_connection_string(os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
            container_name = os.getenv('BRONZE_CONTAINER_NAME', 'bronze-layer')
            blob_client = bsc.get_blob_client(container=container_name, blob=self.blob_path)
            
            # Create a safe temp file on the Mac
            temp_dir = tempfile.gettempdir()
            self.local_temp_path = os.path.join(temp_dir, self.filename)
            
            print(f"📥 Downloading {self.filename} from Azure for analysis...")
            with open(self.local_temp_path, "wb") as f:
                f.write(blob_client.download_blob().readall())

    def __del__(self):
        """Automatically cleans up the temp file when analysis is done."""
        if self.local_temp_path and os.path.exists(self.local_temp_path):
            os.remove(self.local_temp_path)
            print(f"🧹 Cleaned up temp file: {self.local_temp_path}")

    def get_metadata(self):
        """Bridge method for the Frontend."""
        try:
            full_meta = self.extract_metadata()
            variables = {}
            rows = full_meta.get('num_rows', 0)
            
            for col_name, stats in full_meta.get('columns', {}).items():
                variables[col_name] = {
                    'shape': (rows,),          
                    'dtype': stats['detected_type'] 
                }
                
            return {
                'filename': self.filename,
                'file_type': 'CSV (Smart Analysis)',
                'variables': variables
            }
        except Exception as e:
            return {'error': str(e)}

    def read_file(self):
        self._download_from_azure() # Ensure file is downloaded first
        
        for sep in [',', ';', '\t', '|']:
            try:
                # Use the local_temp_path instead of the old filepath
                self.df = pd.read_csv(self.local_temp_path, sep=sep, engine='python')
                if len(self.df.columns) == 1 and sep == ',':
                    continue
                print(f"✅ Read {self.filename} with separator '{sep}'")
                return self.df
            except Exception:
                continue
        raise ValueError(f"Could not parse {self.filename}")

    # --- YOUR DYNAMIC LOGIC REMAINS EXACTLY THE SAME BELOW THIS LINE ---

    @staticmethod
    def _classify_column(series):
        if series.dtype == bool or set(series.dropna().unique()).issubset(
            {True, False, 0, 1, 'true', 'false', 'True', 'False', 'yes', 'no', 'Yes', 'No'}
        ):
            if series.nunique() <= 2:
                return 'boolean'

        if pd.api.types.is_numeric_dtype(series):
            name_lower = series.name.lower()
            time_keywords = ['time', 'timestamp', 'date', 'epoch', 'unix', 'sec', 'ms', 'ns']
            if any(kw in name_lower for kw in time_keywords):
                return 'timestamp'
            if series.min() > 1e9 and series.is_monotonic_increasing:
                return 'timestamp'
            return 'numeric'

        if series.dtype == object:
            try:
                pd.to_datetime(series.head(20), infer_datetime_format=True)
                return 'timestamp'
            except (ValueError, TypeError):
                pass

        if series.dtype == object:
            unique_ratio = series.nunique() / max(len(series), 1)
            if unique_ratio < 0.05 or series.nunique() <= 50:
                return 'categorical'
            return 'text'

        return 'unknown'

    def _stats_for_column(self, col_name):
        series = self.df[col_name]
        col_type = self._classify_column(series)

        base = {
            'column_name': col_name,
            'detected_type': col_type,
            'dtype': str(series.dtype),
            'total_values': int(len(series)),
            'null_count': int(series.isnull().sum()),
            'non_null_count': int(series.notna().sum()),
            'unique_values': int(series.nunique()),
            'sample_values': [_safe_serialize(v) for v in series.dropna().head(5).tolist()]
        }

        if col_type == 'numeric':
            base.update({
                'min': _safe_float(series.min()),
                'max': _safe_float(series.max()),
                'mean': _safe_float(series.mean()),
                'median': _safe_float(series.median()),
                'std': _safe_float(series.std()),
                'percentile_25': _safe_float(series.quantile(0.25)),
                'percentile_75': _safe_float(series.quantile(0.75)),
            })

        elif col_type == 'timestamp':
            try:
                dt = pd.to_datetime(series, unit='s' if series.dtype.kind in 'ifu' else None, errors='coerce')
                base.update({
                    'min': str(dt.min()),
                    'max': str(dt.max()),
                    'time_range_seconds': _safe_float((dt.max() - dt.min()).total_seconds()),
                })
            except Exception:
                if pd.api.types.is_numeric_dtype(series):
                    base.update({
                        'min': _safe_float(series.min()),
                        'max': _safe_float(series.max()),
                        'time_range_seconds': _safe_float(series.max() - series.min()),
                    })

        elif col_type == 'categorical':
            counts = series.value_counts().head(10)
            base['top_values'] = [
                {'value': _safe_serialize(v), 'count': int(c)}
                for v, c in counts.items()
            ]

        elif col_type == 'boolean':
            base['true_count'] = int(series.astype(str).str.lower().isin(['true', '1', 'yes']).sum())
            base['false_count'] = int(series.astype(str).str.lower().isin(['false', '0', 'no']).sum())

        elif col_type == 'text':
            lengths = series.dropna().str.len()
            base.update({
                'avg_length': _safe_float(lengths.mean()),
                'min_length': int(lengths.min()) if len(lengths) else 0,
                'max_length': int(lengths.max()) if len(lengths) else 0,
            })

        return base

    def extract_metadata(self):
        if self.df is None:
            self.read_file()

        metadata = {
            'filename': self.filename,
            # Use the local temp file to get the correct size
            'file_size': os.path.getsize(self.local_temp_path), 
            'file_type': 'CSV',
            'num_rows': int(len(self.df)),
            'num_columns': int(len(self.df.columns)),
            'columns': {}
        }

        type_counts = {}

        for col in self.df.columns:
            col_stats = self._stats_for_column(col)
            metadata['columns'][col] = col_stats
            t = col_stats['detected_type']
            type_counts[t] = type_counts.get(t, 0) + 1

        metadata['type_summary'] = type_counts
        metadata['has_nulls'] = int(self.df.isnull().any().any())
        metadata['total_null_cells'] = int(self.df.isnull().sum().sum())

        return metadata

def _safe_float(val):
    try:
        f = float(val)
        return None if (np.isnan(f) or np.isinf(f)) else round(f, 6)
    except (TypeError, ValueError):
        return None

def _safe_serialize(val):
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return None if np.isnan(val) else float(val)
    if isinstance(val, (np.bool_,)):
        return bool(val)
    return str(val)