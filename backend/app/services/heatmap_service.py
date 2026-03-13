from typing import List, Dict
from collections import defaultdict


def compute_heatmap(points: List[Dict]) -> List[Dict]:
    """
    Group complaint coordinates into grid cells (0.01° ≈ 1 km) and
    return a list of {lat, lon, intensity} dicts for the frontend heatmap layer.

    Args:
        points: list of dicts with keys 'latitude' and 'longitude'

    Returns:
        list of heatmap points with intensity proportional to complaint count
    """
    if not points:
        return []

    BUCKET_SIZE = 0.01  # degrees (~1 km grid)
    buckets: Dict[tuple, int] = defaultdict(int)

    for p in points:
        lat = p.get("latitude")
        lon = p.get("longitude")
        if lat is None or lon is None:
            continue
        # Snap to nearest grid cell
        bucket_lat = round(round(lat / BUCKET_SIZE) * BUCKET_SIZE, 4)
        bucket_lon = round(round(lon / BUCKET_SIZE) * BUCKET_SIZE, 4)
        buckets[(bucket_lat, bucket_lon)] += 1

    if not buckets:
        return []

    max_count = max(buckets.values())

    heatmap = []
    for (lat, lon), count in buckets.items():
        heatmap.append({
            "lat": lat,
            "lon": lon,
            "intensity": round(count / max_count, 4),  # normalise 0–1
            "count": count,
        })

    # Sort by intensity descending so the frontend can optionally limit results
    heatmap.sort(key=lambda x: x["intensity"], reverse=True)
    return heatmap
