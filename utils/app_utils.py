import glob
import os

def find_file_by_stem(folder, stem):
    matches = glob.glob(os.path.join(folder, f"{stem}.*"))
    return matches[0] if matches else None