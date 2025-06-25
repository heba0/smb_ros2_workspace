import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

# Load CSV
df = pd.read_csv('sample_input.csv')

# Filter out low-likelihood detections (optional threshold)
#df = df[df['likelihood'] > 0.8]

results = []

# Process each label separately
for label in df['label'].unique():
    label_data = df[df['label'] == label].copy()  # safe copy
    coords = label_data[['x', 'y', 'z']].values

    clustering = DBSCAN(eps=0.5, min_samples=2).fit(coords)
    label_data.loc[:, 'cluster_id'] = clustering.labels_


    # Ignore noise points (cluster_id == -1)
    clustered = label_data[label_data['cluster_id'] != -1]

    # Get mean coordinates per cluster
    for cluster_id, group in clustered.groupby('cluster_id'):
        mean_coords = group[['x', 'y', 'z']].mean().to_dict()
        total_likelihood = group['likelihood'].sum()  # <-- new line

        results.append({
            'label': label,
            'cluster_id': int(cluster_id),
            'mean_x': mean_coords['x'],
            'mean_y': mean_coords['y'],
            'mean_z': mean_coords['z'],
            'num_points': len(group),
            'sum_likelihood': total_likelihood  # <-- new column
        })

# Convert result to DataFrame
result_df = pd.DataFrame(results)

# Save to CSV or print
result_df.to_csv('clustered_objects.csv', index=False)
print(result_df)
