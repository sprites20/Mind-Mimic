import numpy as np
from PIL import Image
from pyzfp import compress, decompress
import gzip
import shutil
import os

the_file = 'cover1.jpg'

# Read the image file directly into a NumPy array with float32 data type
image_array_float32 = np.fromfile(the_file, dtype=np.float32)

# Reshape the array to match the dimensions of the original image
# Replace (height, width, channels) with the actual dimensions and channels of your image
#image_array_float32 = image_array_float32.reshape((height, width, channels))

# Compress the float32 image array using pyzfp
tolerance = 1
parallel = True
compressed_image = compress(image_array_float32, tolerance=tolerance, parallel=parallel)

# Decompress the compressed data to verify correctness
recovered_image = decompress(compressed_image, image_array_float32.shape, image_array_float32.dtype, tolerance=tolerance)

# Calculate compression ratio
original_size = image_array_float32.nbytes
compressed_size = len(compressed_image)
compression_ratio = original_size / compressed_size

# Print information
print(f"Original Size: {original_size} bytes")
print(f"Compressed Size: {compressed_size} bytes")
print(f"Compression Ratio: {compression_ratio:.2f}")


# Read the image file into memory
with open(the_file, 'rb') as f:
    data = f.read()

# Compress the data using gzip
with gzip.open('compressed_image.gz', 'wb') as f:
    f.write(data)

# Calculate compression ratio
original_size = len(data)
compressed_size = os.path.getsize('compressed_image.gz')
compression_ratio = compressed_size / original_size

# Print information
print(f"Original Size: {original_size} bytes")
print(f"Compressed Size: {compressed_size} bytes")
print(f"Compression Ratio: {compression_ratio:.2f}")