import pandas as pd

# Allowed classes
allowed_classes = {"clock", "umbrella", "backpack", "stop sign", "bottle"}

def filter_similar_instances(input_path, output_path, dx=0.2, dy=0.2, dz=0.2):
    """
    Filters CSV rows by class and removes consecutive duplicates
    based on thresholds in x, y, and z.
    """
    df = pd.read_csv(input_path)

    # Step 1: Filter allowed classes
    df = df[df['class'].isin(allowed_classes)].reset_index(drop=True)

    # Step 2: Initialize output with first row
    filtered_rows = [df.iloc[0]]

    # Step 3: Loop through and compare with previous row of the same class
    for i in range(1, len(df)):
        curr = df.iloc[i]
        prev = filtered_rows[-1]

        if curr['class'] == prev['class']:
            if (
                abs(curr['x'] - prev['x']) < dx and
                abs(curr['y'] - prev['y']) < dy and
                abs(curr['z'] - prev['z']) < dz
            ):
                continue  # Skip as it's too similar
        filtered_rows.append(curr)

    # Step 4: Save filtered results
    df_filtered = pd.DataFrame(filtered_rows)
    df_filtered.to_csv(output_path, index=False)
    print(f"Filtered data saved to {output_path}")

# Example usage:
filter_similar_instances('detections_world.csv', 'detections_filtered.csv', dx=0.2, dy=0.2, dz=0.2)
