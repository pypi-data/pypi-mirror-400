import numpy as np
from pathlib import Path
def npzSave(output, data):
    output = output.replace('.npy', '.npz')
    output_path = Path(output).with_suffix('.npz')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output_path, data=data)
    print(f"{output_path} done")
def npzLoad(output_path):
    return np.load(Path(output_path).with_suffix('.npz'))['data']

"""
npzSave(output, data)
npzLoad(output_path)
"""