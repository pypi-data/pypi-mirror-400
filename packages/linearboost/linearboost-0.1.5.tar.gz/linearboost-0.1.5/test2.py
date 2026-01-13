import minio, openml, inspect

print("MinIO version:", getattr(minio, "__version__", "unknown"))
print("MinIO location:", minio.__file__)
print("OpenML version:", getattr(openml, "__version__", "unknown"))
print("fget_object signature:", inspect.signature(minio.Minio.fget_object))

