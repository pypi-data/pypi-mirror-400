import os


# Utility function to check if the code is running in Google Colab
def is_colab():
    try:
        import google.colab  # noqa: F401
        return True
    except ImportError:
        return False


def get_base_data_dir():
    """Get the base directory for storing data"""
    if is_colab():
        print("Current environment is Google Colab, mounting Google Drive...")
        from google.colab import drive
        # Try to mount Google Drive, skip if already mounted
        if not os.path.exists('/content/drive'):
            drive.mount('/content/drive')

        # Define the data directory path in Google Drive
        base_dir = os.path.join('/content/drive', 'MyDrive', 'data')
        # Create the directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
        print(f"Google Drive data directory ready: {base_dir}")
        return base_dir
    else:
        print("Current environment is not Google Colab, using local data directory.")
        # Use user's home directory as the root for data storage
        base_dir = os.path.join(os.path.expanduser('~'), 'data')
        os.makedirs(base_dir, exist_ok=True)
        print(f"Local data directory ready: {base_dir}")
        return base_dir


def flush_drive():
    if is_colab():
        from google.colab import drive
        drive.flush_and_unmount()
        print('Google Drive has been flushed')
    else:
        print('Not running in Google Colab')


# ==================== Main Program ====================
if __name__ == "__main__":
    # 1. check if running in colab
    if is_colab():
        print("Running in Google Colab")
    else:
        print("Not running in Google Colab")

    # 2. get base data directory
    base_data_directory = get_base_data_dir()
    print(f"Data will be stored in: {base_data_directory}")

    # 3. flush drive
    flush_drive()
