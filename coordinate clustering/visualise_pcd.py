#!/usr/bin/env python3
import argparse

import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d
import pandas as pd


def make_map(pcd_path, voxel, point_size, alpha):
    cloud = o3d.io.read_point_cloud(pcd_path)
    if voxel:
        cloud = cloud.voxel_down_sample(voxel)
    mat = o3d.visualization.rendering.MaterialRecord()
    mat.shader = "defaultUnlit"
    mat.base_color = (0, 0, 1, alpha)  # translucent blue
    mat.point_size = point_size
    return cloud, mat

def compute_distances_to_map_pts(detection_pts, map_pts_tree):
    dists = []
    for pt in detection_pts:
        [_, idx, dist_sq] = map_pts_tree.search_knn_vector_3d(pt, 1)
        dist = np.sqrt(dist_sq[0])
        dists.append(dist)
    return np.array(dists)

def dist_to_color(distances, cmap_name="jet", vmin=None, vmax=None):
    # Normalize distances for colormap (smaller distance = hotter color)
    if vmin is None:
        vmin = distances.min()
    if vmax is None:
        vmax = distances.max()
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap(cmap_name)
    colors = cmap(1 - norm(distances))[:, :3]  # invert: close = red
    return colors

def make_objects_colored(csv_path, radius, map_pts_tree):
    df = pd.read_csv(csv_path)
    xyz = df[["x", "y", "z"]].to_numpy(float)
    labs = df["class"].astype(str).tolist()

    # Compute distances to nearest map points
    dists = compute_distances_to_map_pts(xyz, map_pts_tree)
    colors = dist_to_color(dists, cmap_name="jet")

    merged_mesh = None
    for i, center in enumerate(xyz):
        sph = o3d.geometry.TriangleMesh.create_sphere(radius)
        sph.translate(center)
        sph.paint_uniform_color(colors[i])
        merged_mesh = sph if merged_mesh is None else merged_mesh + sph

    merged_mesh.compute_vertex_normals()
    mat = o3d.visualization.rendering.MaterialRecord()
    mat.shader = "defaultLit"

    return merged_mesh, mat, xyz, labs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pcd", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--map_voxel", type=float, default=0.05)
    ap.add_argument("--map_pts", type=float, default=1.0)
    ap.add_argument("--radius", type=float, default=0.15)
    args = ap.parse_args()

    map_geo, map_mat = make_map(args.pcd, args.map_voxel, args.map_pts, alpha=0.4)

    # Build KD-tree from map points
    map_kdtree = o3d.geometry.KDTreeFlann(map_geo)

    obj_mesh, obj_mat, pts, lbl = make_objects_colored(args.csv, args.radius, map_kdtree)

    app = o3d.visualization.gui.Application.instance
    app.initialize()
    vis = o3d.visualization.O3DVisualizer("Map + Heatmap Objects", 1280, 800)

    vis.add_geometry("map", map_geo, map_mat)
    vis.add_geometry("objects", obj_mesh, obj_mat)

    z_off = np.array([0, 0, args.radius * 1.2])
    for p, t in zip(pts, lbl):
        vis.add_3d_label(p + z_off, t)

    vis.reset_camera_to_default()
    app.add_window(vis)
    app.run()

if __name__ == "__main__":
    main()
