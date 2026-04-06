import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True' 
import pymssql
import pytz
import pandas as pd
import numpy as np
from io import BytesIO
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

class SilverService:
    def __init__(self):
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.bronze_container  = os.getenv('BRONZE_CONTAINER_NAME', 'bronze-layer')
        self.silver_container  = 'silver-layer' 
        self.bsc = BlobServiceClient.from_connection_string(self.connection_string)

    def get_db_connection(self):
        return pymssql.connect(
            server   = os.getenv("AZURE_SQL_SERVER"),
            user     = os.getenv("AZURE_SQL_USER"),
            password = os.getenv("AZURE_SQL_PASSWORD"),
            database = os.getenv("AZURE_SQL_DATABASE"),
            as_dict  = True
        )

    def process_csv_to_parquet(self, bronze_file_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM bronze_files WHERE id = %s", (bronze_file_id,))
            bronze_file = cursor.fetchone()

            if not bronze_file or bronze_file['file_extension'] != 'csv':
                print("Invalid file or not a CSV.")
                return False

            blob_path = bronze_file['file_path']
            print(f"🔄 Processing Bronze File: {blob_path}")

            bronze_client = self.bsc.get_blob_client(container=self.bronze_container, blob=blob_path)
            download_stream = bronze_client.download_blob().readall()
            
            df = pd.read_csv(BytesIO(download_stream))
            
            df.dropna(how='all', inplace=True) 
            df.dropna(axis=1, how='all', inplace=True) 
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_') 
            
            row_count = len(df)
            schema_str = ", ".join(df.columns)

            # 🚨 --- SENSOR SEGREGATION LOGIC ---
            search_string = (schema_str + " " + bronze_file['filename']).lower()
            if 'chirp' in search_string:
                sensor_type = 'Radar'
            else:
                sensor_type = 'WiFi' # Default for CSV if no chirp
            print(f"🏷️ Categorized as: {sensor_type}")

            parquet_io = BytesIO()
            df.to_parquet(parquet_io, engine='pyarrow', index=False)
            parquet_io.seek(0)
            parquet_size = parquet_io.getbuffer().nbytes

            silver_filename = bronze_file['filename'].replace('.csv', '.parquet')
            silver_blob_path = blob_path.replace('.csv', '.parquet') 
            
            silver_client = self.bsc.get_blob_client(container=self.silver_container, blob=silver_blob_path)
            silver_client.upload_blob(parquet_io, overwrite=True)

            raw_time = bronze_file['raw_upload_time']
            timezone_str = bronze_file['upload_timezone'] or 'America/New_York'
            try:
                local_tz = pytz.timezone(timezone_str)
                localized_time = local_tz.localize(raw_time)
                standardized_utc_time = localized_time.astimezone(pytz.utc)
            except:
                standardized_utc_time = raw_time 

            # 🚨 UPDATE SQL TO INCLUDE SENSOR TYPE
            cursor.execute("""
                INSERT INTO silver_files (bronze_file_id, filename, file_path, file_size, row_count, columns_schema, standardized_upload_time_utc, sensor_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (bronze_file_id, silver_filename, silver_blob_path, parquet_size, row_count, schema_str, standardized_utc_time, sensor_type))

            cursor.execute("""
                INSERT INTO data_lineage (bronze_file_id, source_dataset, source_file_path, transformation_type, status)
                VALUES (%s, %s, %s, 'bronze_to_silver_parquet', 'success')
            """, (bronze_file_id, bronze_file['dataset_name'], silver_blob_path))

            cursor.execute("UPDATE bronze_files SET processing_status = 'silver_processed', sensor_type = %s WHERE id = %s", (sensor_type, bronze_file_id))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"❌ Silver Transformation Failed: {e}")
            cursor.execute("INSERT INTO data_lineage (bronze_file_id, transformation_type, status, details) VALUES (%s, 'bronze_to_silver_parquet', 'failed', %s)", (bronze_file_id, str(e)))
            conn.commit()
            return False
        finally:
            conn.close()

    def process_mat_to_silver(self, bronze_file_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        from backend.processors.mat_processor import WirelessDataProcessor
        local_tmp_path = None

        try:
            cursor.execute("SELECT * FROM bronze_files WHERE id = %s", (bronze_file_id,))
            bronze_file = cursor.fetchone()

            if not bronze_file or bronze_file['file_extension'] != 'mat':
                return False

            blob_path = bronze_file['file_path']
            filename = bronze_file['filename']
            
            local_tmp_path = os.path.join('/tmp', filename.replace('/', '_'))
            bronze_client = self.bsc.get_blob_client(container=self.bronze_container, blob=blob_path)
            
            with open(local_tmp_path, "wb") as download_file:
                download_file.write(bronze_client.download_blob().readall())
            
            processor = WirelessDataProcessor(local_tmp_path)
            data_dict = processor.read_file()  
            
            clean_dict = {k: v for k, v in data_dict.items() if not k.startswith('__')}
            flattened_data = {}
            max_len = 0
            
            for key, val in clean_dict.items():
                if isinstance(val, np.ndarray):
                    is_complex = np.iscomplexobj(val) or (val.dtype.names and 'real' in val.dtype.names and 'imag' in val.dtype.names)
                    if is_complex:
                        if np.iscomplexobj(val):
                            flat_real, flat_imag = val.real.flatten(), val.imag.flatten()
                        else:
                            flat_real, flat_imag = val['real'].flatten(), val['imag'].flatten()
                        flattened_data[f"{key}_real"] = flat_real
                        flattened_data[f"{key}_imag"] = flat_imag
                        if len(flat_real) > max_len: max_len = len(flat_real)
                    else:
                        flat_val = val.flatten()
                        flattened_data[key] = flat_val
                        if len(flat_val) > max_len: max_len = len(flat_val)
                else:
                    flattened_data[key] = [val]
                    if max_len == 0: max_len = 1

            for key in flattened_data:
                current_len = len(flattened_data[key])
                if current_len < max_len:
                    flattened_data[key] = np.concatenate((flattened_data[key], [np.nan] * (max_len - current_len)))

            df = pd.DataFrame(flattened_data)
            row_count = len(df)
            schema_str = ", ".join(df.columns)

            # 🚨 --- SENSOR SEGREGATION LOGIC ---
            search_string = (schema_str + " " + filename).lower()
            if 'chirp' in search_string:
                sensor_type = 'Radar'
            elif 'rssi' in search_string:
                sensor_type = 'WiFi'
            else:
                sensor_type = 'WiFi' # Default fallback
            print(f"🏷️ Categorized MAT as: {sensor_type}")

            parquet_io = BytesIO()
            df.to_parquet(parquet_io, engine='pyarrow', index=False)
            parquet_io.seek(0)
            parquet_size = parquet_io.getbuffer().nbytes

            silver_filename = filename.replace('.mat', '.parquet')
            silver_blob_path = blob_path.replace('.mat', '.parquet') 
            
            silver_client = self.bsc.get_blob_client(container=self.silver_container, blob=silver_blob_path)
            silver_client.upload_blob(parquet_io, overwrite=True)

            raw_time = bronze_file['raw_upload_time']
            timezone_str = bronze_file['upload_timezone'] or 'America/New_York'
            try:
                local_tz = pytz.timezone(timezone_str)
                standardized_utc_time = local_tz.localize(raw_time).astimezone(pytz.utc)
            except:
                standardized_utc_time = raw_time 

            # 🚨 UPDATE SQL TO INCLUDE SENSOR TYPE
            cursor.execute("""
                INSERT INTO silver_files (bronze_file_id, filename, file_path, file_size, row_count, columns_schema, standardized_upload_time_utc, sensor_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (bronze_file_id, silver_filename, silver_blob_path, parquet_size, row_count, schema_str, standardized_utc_time, sensor_type))

            cursor.execute("INSERT INTO data_lineage (bronze_file_id, source_dataset, source_file_path, transformation_type, status) VALUES (%s, %s, %s, 'bronze_to_silver_mat', 'success')", (bronze_file_id, bronze_file['dataset_name'], silver_blob_path))

            cursor.execute("UPDATE bronze_files SET processing_status = 'silver_processed', sensor_type = %s WHERE id = %s", (sensor_type, bronze_file_id))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"❌ Silver Transformation Failed for {bronze_file_id}: {e}")
            cursor.execute("INSERT INTO data_lineage (bronze_file_id, transformation_type, status, details) VALUES (%s, 'bronze_to_silver_mat', 'failed', %s)", (bronze_file_id, str(e)))
            conn.commit()
            return False
            
        finally:
            if local_tmp_path and os.path.exists(local_tmp_path): os.remove(local_tmp_path)
            conn.close()

    def process_pcd_to_silver(self, bronze_file_id):
        import os, pandas as pd, numpy as np
        from io import BytesIO
        from backend.processors.pcd_processor import PCDProcessor 
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        local_tmp_path = None

        try:
            cursor.execute("SELECT * FROM bronze_files WHERE id = %s", (bronze_file_id,))
            bronze_file = cursor.fetchone()

            if not bronze_file or bronze_file['file_extension'] != 'pcd': return False

            blob_path = bronze_file['file_path']
            filename = bronze_file['filename']
            
            local_tmp_path = os.path.join('/tmp', filename.replace('/', '_'))
            bronze_client = self.bsc.get_blob_client(container=self.bronze_container, blob=blob_path)
            
            with open(local_tmp_path, "wb") as download_file:
                download_file.write(bronze_client.download_blob().readall())
            
            processor = PCDProcessor(local_tmp_path)
            df = processor.read_file()
            if df is None or df.empty: raise ValueError("Could not extract data from PCD file.")

            original_points = len(df)
            voxel_size = 0.1 
            x_col, y_col, z_col = df.columns[0], df.columns[1], df.columns[2]
            
            df['voxel_x'] = (df[x_col] / voxel_size).round()
            df['voxel_y'] = (df[y_col] / voxel_size).round()
            df['voxel_z'] = (df[z_col] / voxel_size).round()
            
            downsampled_df = df.groupby(['voxel_x', 'voxel_y', 'voxel_z']).mean().reset_index().drop(columns=['voxel_x', 'voxel_y', 'voxel_z'])
            new_points = len(downsampled_df)

            row_count = len(downsampled_df)
            schema_str = ", ".join(downsampled_df.columns)

            # 🚨 --- SENSOR SEGREGATION LOGIC ---
            sensor_type = 'LiDAR' # PCD is always LiDAR
            print(f"🏷️ Categorized PCD as: {sensor_type}")

            parquet_io = BytesIO()
            downsampled_df.to_parquet(parquet_io, engine='pyarrow', index=False)
            parquet_io.seek(0)
            parquet_size = parquet_io.getbuffer().nbytes

            silver_filename = filename.replace('.pcd', '.parquet')
            silver_blob_path = blob_path.replace('.pcd', '.parquet') 
            
            silver_client = self.bsc.get_blob_client(container=self.silver_container, blob=silver_blob_path)
            silver_client.upload_blob(parquet_io, overwrite=True)

            raw_time = bronze_file['raw_upload_time']
            timezone_str = bronze_file['upload_timezone'] or 'America/New_York'
            try:
                standardized_utc_time = pytz.timezone(timezone_str).localize(raw_time).astimezone(pytz.utc)
            except:
                standardized_utc_time = raw_time 

            # 🚨 UPDATE SQL TO INCLUDE SENSOR TYPE
            cursor.execute("""
                INSERT INTO silver_files (bronze_file_id, filename, file_path, file_size, row_count, columns_schema, standardized_upload_time_utc, sensor_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (bronze_file_id, silver_filename, silver_blob_path, parquet_size, row_count, schema_str, standardized_utc_time, sensor_type))

            compression_details = f"Voxel Size: {voxel_size}m | Points: {original_points} -> {new_points}"
            cursor.execute("INSERT INTO data_lineage (bronze_file_id, source_dataset, source_file_path, transformation_type, status, details) VALUES (%s, %s, %s, 'bronze_to_silver_pcd', 'success', %s)", (bronze_file_id, bronze_file['dataset_name'], silver_blob_path, compression_details))

            cursor.execute("UPDATE bronze_files SET processing_status = 'silver_processed', sensor_type = %s WHERE id = %s", (sensor_type, bronze_file_id))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"❌ Silver Transformation Failed for {bronze_file_id}: {e}")
            cursor.execute("INSERT INTO data_lineage (bronze_file_id, transformation_type, status, details) VALUES (%s, 'bronze_to_silver_pcd', 'failed', %s)", (bronze_file_id, str(e)))
            conn.commit()
            return False
            
        finally:
            if local_tmp_path and os.path.exists(local_tmp_path): os.remove(local_tmp_path)
            conn.close()