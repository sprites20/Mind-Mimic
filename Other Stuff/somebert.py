import nltk
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt

# Download the nltk punkt tokenizer data (you need to do this once)
nltk.download('punkt')

# Load a pre-trained SBERT model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Example string

# Tokenize the string into sentences
sentences = nltk.sent_tokenize(text)
# Print the number of sentences
print(f"Number of sentences: {len(sentences)}")
print(sentences)
# Compute SBERT embeddings for all sentences
embeddings = model.encode(sentences, convert_to_tensor=True)
print(embeddings.shape)
# Move the embeddings to the CPU before fitting KMeans
embeddings_cpu = embeddings.cpu().numpy()

# Evaluate different numbers of clusters
inertia_values = []
for num_clusters in range(1, 11):  # Test from 1 to 10 clusters
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(embeddings_cpu)
    inertia_values.append(kmeans.inertia_)

# Find the "elbow" point
elbow_point = None
for i in range(1, len(inertia_values) - 1):
    if inertia_values[i - 1] - inertia_values[i] > 0.1 * (inertia_values[i] - inertia_values[i + 1]):
        elbow_point = i + 1
        break

# Plot the elbow curve
plt.plot(range(1, 11), inertia_values, marker='o')
plt.title('Elbow Method for Optimal Number of Clusters')
plt.xlabel('Number of Clusters')
plt.ylabel('Inertia (Within-Cluster Sum of Squares)')

# Highlight the elbow point
if elbow_point is not None:
    plt.scatter(elbow_point, inertia_values[elbow_point - 1], color='red', marker='x', label='Elbow Point')

plt.legend()
plt.show()