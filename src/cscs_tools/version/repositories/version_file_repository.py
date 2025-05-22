import json
import os

from cscs_tools.version.models.entities.version import Version

def find_version_json(filename="version.json", max_levels=5):
    current_dir = os.getcwd()
    for _ in range(max_levels):
        candidate = os.path.join(current_dir, filename)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current_dir)
        if parent == current_dir:  # reached root
            break
        current_dir = parent
    raise VersionFileNotFoundError(f"{filename} not found in cwd or parent directories.")


class VersionFileRepository:
    def __init__(self, filename=None):
        if filename:
            self.path = filename
        else:
            self.path = find_version_json()
        self.path = os.path.abspath(self.path)

    def get_version(self):
        if not os.path.isfile(self.path):
            raise VersionFileNotFoundError(
                f"""
Version file not found at the root directory.
Expected a JSON file like: 
{{
    \"major\": 0, 
    \"minor\": 2, 
    \"patch\": 1, 
    \"inherit\": true
}}

Either create it at your project root or specify its path like:

service = VersionService(file='path/to/version.json')
"""
            )

        try:
            with open(self.path) as json_file:
                version_dict = json.load(json_file)
                return Version(version_dict)
        except FileNotFoundError:
            return None

    def save(self, version):
        with open(self.path, "w") as json_file:
            json.dump(version.__dict__, json_file)
        return True


class VersionFileNotFoundError(Exception):
    """Custom exception for missing version file."""
    pass