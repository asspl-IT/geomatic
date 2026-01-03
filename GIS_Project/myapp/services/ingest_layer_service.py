from myapp.services.vector_ingest import ingest_vector
from myapp.services.raster_ingest import ingest_raster

def ingest_layer(layer_def, project):
    path = layer_def["full_path"]
    ltype = layer_def["type"]

    if ltype == "vector":
        ingest_vector(path, project)

    elif ltype == "raster":
        ingest_raster(path, project)

    else:
        raise ValueError(f"Unsupported layer type {ltype}")
