import os
import json
import importlib.resources

class AssetNotFoundError(FileNotFoundError):
    pass

def confirm_action(message):
    resp = input(f"{message} [y/N]: ").strip().lower()
    return resp == 'y'

class AssetsManager:
    """
    Manages JSON assets inside the progressive_py/assets directory.
    Uses importlib.resources for robust access after installation (read-only).
    For writing, uses the source assets folder next to this file.
    """

    def __init__(self, package="progressive_py", assets_folder="assets"):
        self.package = package
        self.assets_folder = assets_folder
        self.show_msg = False
        # Filesystem path for writing (source tree)
        self.fs_assets_folder = os.path.join(os.path.dirname(__file__), assets_folder)

    def _get_asset_path(self, category, file_key):
        return f"{self.assets_folder}/{category}/{file_key}.json"

    def _get_fs_asset_path(self, category, file_key):
        return os.path.join(self.fs_assets_folder, category, f"{file_key}.json")

    def load(self, category, file_key, name):
        asset_path = self._get_asset_path(category, file_key)
        try:
            with importlib.resources.files(self.package).joinpath(asset_path).open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise AssetNotFoundError(f"File '{file_key}.json' not found in '{category}'")
        if name not in data:
            raise AssetNotFoundError(f"Asset '{name}' not found in '{file_key}.json'")
        if self.show_msg:
            print(f"✅ Loaded '{name}' from '{category}/{file_key}.json'")
        return data[name]

    def save(self, content, category, file_key, name):
        fs_path = self._get_fs_asset_path(category, file_key)
        os.makedirs(os.path.dirname(fs_path), exist_ok=True)
        try:
            with open(fs_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        data[name] = content
        with open(fs_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        if self.show_msg:
            print(f"✅ Saved '{name}' to '{category}/{file_key}.json'")

    def delete(self, category, file_key, name):
        if not confirm_action(f"Delete asset '{name}' from '{category}/{file_key}.json'?"):
            print("❌ Delete cancelled.")
            return
        fs_path = self._get_fs_asset_path(category, file_key)
        try:
            with open(fs_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise AssetNotFoundError(f"File '{file_key}.json' not found in '{category}'")
        if name not in data:
            raise AssetNotFoundError(f"Asset '{name}' not found in '{file_key}.json'")
        del data[name]
        with open(fs_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        if self.show_msg:
            print(f"🗑️ Deleted '{name}' from '{category}/{file_key}.json'")

    def rename(self, category, file_key, old_name, new_name):
        if not confirm_action(f"Rename asset '{old_name}' to '{new_name}' in '{category}/{file_key}.json'?"):
            print("❌ Rename cancelled.")
            return
        fs_path = self._get_fs_asset_path(category, file_key)
        try:
            with open(fs_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise AssetNotFoundError(f"File '{file_key}.json' not found in '{category}'")
        if old_name not in data:
            raise AssetNotFoundError(f"Asset '{old_name}' not found")
        if new_name in data:
            raise ValueError(f"Asset '{new_name}' already exists")
        data[new_name] = data.pop(old_name)
        with open(fs_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        if self.show_msg:
            print(f"✏️ Renamed '{old_name}' → '{new_name}'")

    def list_assets(self, category, file_key):
        asset_path = self._get_asset_path(category, file_key)
        try:
            with importlib.resources.files(self.package).joinpath(asset_path).open("r", encoding="utf-8") as f:
                data = json.load(f)
            return list(data.keys())
        except FileNotFoundError:
            raise AssetNotFoundError(f"File '{file_key}.json' not found in '{category}'")

    def list_files(self, category):
        folder_path = f"{self.assets_folder}/{category}"
        try:
            files = [p.name for p in importlib.resources.files(self.package).joinpath(folder_path).iterdir() if p.name.endswith(".json")]
            return files
        except Exception:
            raise AssetNotFoundError(f"Category '{category}' not found")

    def list_categories(self):
        try:
            cats = [p.name for p in importlib.resources.files(self.package).joinpath(self.assets_folder).iterdir() if p.is_dir()]
            return cats
        except Exception:
            raise AssetNotFoundError("No categories found")