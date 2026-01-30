import h5py
import numpy as np
import os

class WirelessDataProcessor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.data = {}
        
    def read_file(self):
        with h5py.File(self.filepath, 'r') as f:
            print(f"\n📂 {self.filename}")
            print(f"   Variables: {list(f.keys())}\n")
            
            for key in f.keys():
                if not key.startswith('#'):
                    item = f[key]
                    if isinstance(item, h5py.Dataset):
                        self.data[key] = np.array(item)
                        print(f"   • {key}: {item.shape} ({item.dtype})")
        
        return self.data

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        processor = WirelessDataProcessor(sys.argv[1])
        processor.read_file()
