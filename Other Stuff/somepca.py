import librosa
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Function to extract MFCC features from an audio file
def extract_mfcc(audio_path, max_frames=100):
    audio, sr = librosa.load(audio_path, sr=None)
    
    # Extract MFCC features
    mfcc = librosa.feature.mfcc(audio, sr=sr, n_mfcc=13)

    # Pad or truncate features to a fixed number of frames
    if mfcc.shape[1] < max_frames:
        mfcc = np.pad(mfcc, ((0, 0), (0, max_frames - mfcc.shape[1])))
    else:
        mfcc = mfcc[:, :max_frames]

    return mfcc

# Function to apply PCA to an audio file
def apply_pca(audio_features, n_components=2):
    # Standardize features
    scaler = StandardScaler()
    standardized_features = scaler.fit_transform(audio_features)

    # Apply PCA
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(standardized_features)

    return pca_result

# Calculate dot product similarity between two PCA representations
def calculate_dot_product_similarity(pca_result1, pca_result2):
    similarity = np.dot(pca_result1.flatten(), pca_result2.flatten())
    return similarity

# Example: Compare two audio files
audio_path1 = "oh-my-god-104662.mp3"
audio_path2 = "what-are-you-doing-22344.mp3"

# Extract MFCC features
mfcc1 = extract_mfcc(audio_path1)
mfcc2 = extract_mfcc(audio_path2)

# Apply PCA
pca_result1 = apply_pca(mfcc1)
pca_result2 = apply_pca(mfcc2)

# Calculate dot product similarity
similarity = calculate_dot_product_similarity(pca_result1, pca_result2)

print("Dot Product Similarity:", similarity)
