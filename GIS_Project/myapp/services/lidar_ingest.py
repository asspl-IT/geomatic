import laspy


def ingest_lidar(file_path):
    las = laspy.read(file_path)
    return {
        "points": las.header.point_count,
        "bounds": {
            "xmin": las.header.mins[0],
            "ymin": las.header.mins[1],
            "zmin": las.header.mins[2],
            "xmax": las.header.maxs[0],
            "ymax": las.header.maxs[1],
            "zmax": las.header.maxs[2],
        }
    }
