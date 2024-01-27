import numpy as np
from matplotlib.image import imread
import matplotlib.pyplot as plt
import cv2
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error
import math
from pyzfp import compress

# Load the original image
img = imread("cover1.jpg")

# Split the image into color channels
blue, green, red = cv2.split(img)

# Scale the color channels to the range [0, 1]
df_blue = blue / 255.0
df_green = green / 255.0
df_red = red / 255.0

# Perform PCA on each color channel
n_components = 50  # Adjust the number of components as needed
pca_b = PCA(n_components=n_components)
pca_g = PCA(n_components=n_components)
pca_r = PCA(n_components=n_components)

trans_pca_b = pca_b.fit_transform(df_blue)
trans_pca_g = pca_g.fit_transform(df_green)
trans_pca_r = pca_r.fit_transform(df_red)

# Perform inverse transform to reconstruct the color channels
reconstructed_blue = pca_b.inverse_transform(trans_pca_b)
reconstructed_green = pca_g.inverse_transform(trans_pca_g)
reconstructed_red = pca_r.inverse_transform(trans_pca_r)

# Rescale the reconstructed color channels back to the original scale [0, 255]
reconstructed_blue = np.clip(reconstructed_blue * 255, 0, 255).astype(np.uint8)
reconstructed_green = np.clip(reconstructed_green * 255, 0, 255).astype(np.uint8)
reconstructed_red = np.clip(reconstructed_red * 255, 0, 255).astype(np.uint8)

# Merge the reconstructed color channels into an RGB image
reconstructed_image_rgb = cv2.merge([reconstructed_red, reconstructed_green, reconstructed_blue])
reconstructed_image_rgb_pca = cv2.merge([trans_pca_b, trans_pca_g, trans_pca_r])

# Calculate MSE for each color channel
mse_blue = mean_squared_error(df_blue.flatten(), reconstructed_blue.flatten())
mse_green = mean_squared_error(df_green.flatten(), reconstructed_green.flatten())
mse_red = mean_squared_error(df_red.flatten(), reconstructed_red.flatten())

# Calculate PSNR for each color channel
psnr_blue = 20 * math.log10(1) - 10 * math.log10(mse_blue)
psnr_green = 20 * math.log10(1) - 10 * math.log10(mse_green)
psnr_red = 20 * math.log10(1) - 10 * math.log10(mse_red)

# Calculate the sizes of the original and PCA-transformed matrices in bytes
size_original_matrix = df_blue.nbytes + df_green.nbytes + df_red.nbytes
size_pca_transformed_matrix = trans_pca_b.nbytes + trans_pca_g.nbytes + trans_pca_r.nbytes

# Convert the reconstructed RGB image to float32 and normalize to [0, 1]
reconstructed_image_array = reconstructed_image_rgb.astype(np.float32) / 255.0

# Compress the float32 image array using pyzfp
tolerance = 0.0000001
parallel = True
# Compress the 3D numpy array using ZFP
compressed_data = compress(reconstructed_image_rgb_pca, tolerance=tolerance, parallel=parallel)

# Get the size of the compressed data in bytes
compressed_size_bytes = len(compressed_data)

# Display the comparison
print(f"Size of compressed data: {compressed_size_bytes} bytes")
print(f"Size of original matrices: {size_original_matrix} bytes")
print(f"Size of PCA-transformed matrices: {size_pca_transformed_matrix} bytes")

# Display the original and reconstructed images with MSE and PSNR values
fig, axes = plt.subplots(1, 2, figsize=(12, 8))

# Original image
axes[0].imshow(img)
axes[0].set_title('Original Image')

# Reconstructed image
axes[1].imshow(reconstructed_image_rgb)
axes[1].set_title('Reconstructed Image')

# Add text annotations for MSE and PSNR
mse_text = f'MSE: Blue={mse_blue:.2f}, Green={mse_green:.2f}, Red={mse_red:.2f}'
psnr_text = f'PSNR: Blue={psnr_blue:.2f} dB, Green={psnr_green:.2f} dB, Red={psnr_red:.2f} dB'
fig.text(0.5, 0.05, f'{mse_text}\n{psnr_text}', ha='center', fontsize=12)
# Save an image with JPEG compression and quality 95
cv2.imwrite('compressed_image.jpg', reconstructed_image_rgb, [cv2.IMWRITE_JPEG_QUALITY, 95])
# Show the plot
plt.show()
