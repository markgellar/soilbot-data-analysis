
# cec_data = df[df["cec7_r"].notna()].copy()
# sand_data = df[df["sand_pct"].notna()].copy()
# silt_data = df[df["silt_pct"].notna()].copy()
# clay_data = df[df["clay_pct"].notna()].copy()

# lat_min, lat_max = df["centroid_lat"].min() - 0.05, df["centroid_lat"].max() + 0.05
# lon_min, lon_max = df["centroid_lon"].min() - 0.05, df["centroid_lon"].max() + 0.05
# grid_lon = np.linspace(lon_min, lon_max, 100)
# grid_lat = np.linspace(lat_min, lat_max, 100)
# grid_lon_2d, grid_lat_2d = np.meshgrid(grid_lon, grid_lat)
# county_boundary = unary_union(soilmap.geometry)

# print("Building boundary mask...")
# mask = np.zeros(grid_lon_2d.shape, dtype=bool)
# for i in range(grid_lat_2d.shape[0]):
#     for j in range(grid_lon_2d.shape[1]):
#         pt = ShapelyPoint(grid_lon_2d[i,j], grid_lat_2d[i,j])
#         mask[i,j] = not county_boundary.contains(pt)
# print("Mask built")

# variables = [
#     ("cec7_r",   "CEC (meq/100g)",  "Reds"),
#     ("sand_pct", "Sand (%)",         "Oranges"),
#     ("silt_pct", "Silt (%)",         "Greens"),
#     ("clay_pct", "Clay (%)",         "Blues"),
# ]

# fig, axes = plt.subplots(2, 4, figsize=(20, 10))

# for col_idx, (col, label, cmap) in enumerate(variables):
#     data = df[df[col].notna()].copy()
#     lat = data["centroid_lat"].values
#     lon = data["centroid_lon"].values
#     vals = data[col].values

#     print(f"Kriging {col}: {len(data)} data points")

#     ok = OrdinaryKriging(
#         lon, lat, vals,
#         variogram_model="gaussian",
#         verbose=False,
#         enable_plotting=False
#     )

#     prediction, variance = ok.execute("grid", grid_lon, grid_lat)

#     prediction_masked = np.ma.masked_where(mask, prediction)
#     variance_masked = np.ma.masked_where(mask, variance)

#     # Prediction plotting
#     ax_pred = axes[0, col_idx]
#     im = ax_pred.contourf(grid_lon, grid_lat, prediction_masked, levels=20, cmap=cmap)
#     plt.colorbar(im, ax=ax_pred, label=label)

#     for geom in (county_boundary.geoms if hasattr(county_boundary, 'geoms') else [county_boundary]):
#         x,y = geom.exterior.xy
#         ax_pred.plot(x, y, color="black", linewidth=0.5)

#     ax_pred.scatter(lon, lat, c=vals, cmap=cmap, edgecolors="black", linewidths=0.3, s=20, zorder=5)
#     ax_pred.set_title(f"{label} Kriged")
#     ax_pred.set_xlabel("Longitude")
#     ax_pred.set_ylabel("Latitude")

#     # Variance plotting
#     ax_var = axes[1, col_idx]
#     im2 = ax_var.contourf(grid_lon, grid_lat, variance_masked, levels=20, cmap=cmap)
#     plt.colorbar(im2, ax=ax_var, label=label)

#     for geom in (county_boundary.geoms if hasattr(county_boundary, 'geoms') else [county_boundary]):
#         x,y = geom.exterior.xy
#         ax_var.plot(x, y, color="black", linewidth=0.5)

#     ax_var.scatter(lon, lat, color="black", s=15, zorder=5, alpha=0.5)
#     ax_var.set_title(f"{label} Variance")
#     ax_var.set_xlabel("Longitude")
#     ax_var.set_ylabel("Latitude")

# plt.suptitle("Kriged Soil Properties — Lancaster County PA", fontsize=14)
# plt.tight_layout()
# save_path = Path(__file__).parent / "kriging_all_variables.png"
# plt.savefig(save_path, dpi=150)
# print(f"Done. Filed saved to {save_path}")