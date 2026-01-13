

def fetch_nearest_point(df, tar_lon: float, tar_lat: float, min_dis: float=0):
    """
    找到距离目标点最近的坐标点（距离大于min_dis）
    
    参数:
        df: Polars DataFrame，包含 'lon' 和 'lat' 列
        tar_lon: 目标经度
        tar_lat: 目标纬度
        min_dis: 最小距离阈值

    返回:
        (lon_nearest, lat_nearest): 最近点的经纬度
    """
    import numpy as np
    import polars as pl
    from scipy.spatial import KDTree

    unique_coords = df.select(["lon", "lat"]).unique()
    coords_array = unique_coords.to_numpy()
    tree = KDTree(coords_array)

    target_point = np.column_stack([tar_lon, tar_lat])

    if min_dis > 0:
        # 查询足够多的点以确保找到满足条件的点
        k = min(10, len(coords_array))  # 避免k超过总点数
        distances, indices = tree.query(target_point, k=k)
        
        # 找到第一个距离大于min_dis的点
        valid_mask = distances[0] > min_dis
        if not valid_mask.any():
            raise ValueError(f"未找到距离大于 {min_dis} 的点")
        
        idx = indices[0][valid_mask][0] # type: ignore
    else:
        # 直接查询最近点
        distances, indices = tree.query(target_point, k=1)
        idx = indices[0] # type: ignore

    idx = int(idx)
    # 返回最近点坐标
    lon_nearest = float(unique_coords["lon"][idx])
    lat_nearest = float(unique_coords["lat"][idx])

    return lon_nearest, lat_nearest



if __name__ == "__main__":
    # fetch_nearest_point()
    ...