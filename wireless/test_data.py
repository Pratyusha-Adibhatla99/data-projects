#!/usr/bin/env python3
import os
import scipy.io as sio
import h5py

# Look in channels_release folder
data_dir = 'channels_release'

print("\n" + "="*70)
print("📁 CHECKING YOUR DATA FILES")
print("="*70 + "\n")

if os.path.exists(data_dir):
    files = [f for f in os.listdir(data_dir) if f.endswith('.mat')]
    
    print(f"Found {len(files)} MAT files in {data_dir}/\n")
    
    # Show all filenames
    print("📋 All files:")
    for i, fname in enumerate(files, 1):
        print(f"  {i}. {fname}")
    
    if files:
        print("\n" + "─"*70)
        # Test first file
        test_file = os.path.join(data_dir, files[0])
        print(f"\n🧪 Testing first file: {files[0]}\n")
        
        # Try scipy first
        try:
            data = sio.loadmat(test_file)
            print("✅ File format: MATLAB v7 or earlier (loaded with scipy)")
            
            vars = [k for k in data.keys() if not k.startswith('__')]
            print(f"\n📊 Variables found: {vars}\n")
            
            for var in vars:
                arr = data[var]
                print(f"Variable: {var}")
                print(f"  Shape: {arr.shape}")
                print(f"  Type: {arr.dtype}")
                print(f"  Elements: {arr.size}")
                print()
                
        except NotImplementedError:
            # Try h5py for MATLAB v7.3
            print("✅ File format: MATLAB v7.3+ (HDF5, using h5py)")
            
            with h5py.File(test_file, 'r') as f:
                vars = [k for k in f.keys() if not k.startswith('#')]
                print(f"\n📊 Variables found: {vars}\n")
                
                for key in vars:
                    arr = f[key]
                    print(f"Variable: {key}")
                    print(f"  Shape: {arr.shape}")
                    print(f"  Type: {arr.dtype}")
                    print()
        
        print("="*70)
            
    else:
        print("❌ No .mat files found in channels_release/!")
else:
    print(f"❌ Directory '{data_dir}' doesn't exist!")

print()
