# haralick-torch

GPU-accelerated Haralick texture extraction for GeoTIFF images using PyTorch.

## Installation

GDAL must be installed via precompiled wheels:

https://github.com/cgohlke/geospatial-wheels/releases

```bash
pip install GDAL-3.10.1-cp310-cp310-win_amd64.whl
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install haralick-torch
```

## Usage CLI

```bash
haralick-torch --input image.tif --out-texture textures.tif --out-pca pca.tif --nir-idx 8 --window 7 --levels 128 --tile 64
```

## Usage API
```bash
import torch
from haralick_torch.io import read_nir_as_tensor, write_haralick_geotiff
from haralick_torch.haralick import compute_haralick
from haralick_torch.tiling import process_in_tiles

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ---- INPUT
img = "image.tif"
out = "haralick.tif"
nir_band = 4

# ---- IO
nir, ref_ds = read_nir_as_tensor(img, nir_band, DEVICE)

# ---- HARALICK
textures = process_in_tiles(
    nir,
    compute_haralick,
    window=11,
    stride=1
)

# ---- SAVE
write_haralick_geotiff(
    out,
    textures,
    list(textures.keys()),
    ref_ds
)
```