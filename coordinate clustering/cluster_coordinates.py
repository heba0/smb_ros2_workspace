import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

# Load CSV
df = pd.read_csv("sample_input.csv")

# Optional: Filter low-likelihood values
# df = df[df["likelihood"] > 0.8]

# 🔍 Filter only these classes
allowed_labels = ["bottle", "chair"]
df = df[df["label"].isin(allowed_labels)]

results = []

for label in df["label"].unique():
    label_data = df[df["label"] == label].copy()
    coords = label_data[["x", "y", "z"]].values

    # Apply DBSCAN
    clustering = DBSCAN(eps=0.5, min_samples=2).fit(coords)
    label_data.loc[:, "cluster_id"] = clustering.labels_

    # Filter out noise
    clustered = label_data[label_data["cluster_id"] != -1]

    for cluster_id, group in clustered.groupby("cluster_id"):
        mean_coords = group[["x", "y", "z"]].mean().to_dict()
        sum_likelihood = group["likelihood"].sum()
        avg_likelihood = group["likelihood"].mean()

        results.append(
            {
                "label": label,
                "cluster_id": int(cluster_id),
                "mean_x": mean_coords["x"],
                "mean_y": mean_coords["y"],
                "mean_z": mean_coords["z"],
                "num_points": len(group),
                "sum_likelihood": sum_likelihood,
                "avg_likelihood": avg_likelihood,
                "confidence_score": avg_likelihood,  # same as avg_likelihood for now
            }
        )

# Convert to DataFrame
result_df = pd.DataFrame(results)

# Output
print(result_df)
result_df.to_csv("clustered_filtered_output.csv", index=False)
