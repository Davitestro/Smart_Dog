import os

def get_disk_usage(path="/"):
    statvfs = os.statvfs(path)

    total = statvfs.f_frsize * statvfs.f_blocks      # Total space
    free = statvfs.f_frsize * statvfs.f_bfree        # Free space
    available = statvfs.f_frsize * statvfs.f_bavail  # Available space to non-root

    return  free / (total / 100)

def format_bytes(size):
    # Converts bytes to human-readable format
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


if __name__ == '__main__':
   print(get_disk_usage())
