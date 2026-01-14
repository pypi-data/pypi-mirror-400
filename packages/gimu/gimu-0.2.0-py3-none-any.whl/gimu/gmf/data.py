""" Toolbox for accessing GIM/GMF well data

Use:
    from gmf_data import data_json

    data_json.set_data_folder('/path/to/data')

"""

import json
import os
from collections import OrderedDict

class DataJSON:
    def __init__(self, max_cache_size=10):
        self._data_folders = []
        self._cache = OrderedDict()
        self._max_cache_size = max_cache_size

    def set_data_folders(self, paths):
        self._data_folders = []
        for path in paths:
            self.add_data_folder(path)

    def add_data_folder(self, path):
        if not os.path.isdir(path):
            raise ValueError(f"Path '{path}' is not a valid directory.")
        if path not in self._data_folders:
            self._data_folders.append(path)

    def remove_data_folder(self, path):
        if path in self._data_folders:
            self._data_folders.remove(path)

    def __getitem__(self, well_name):
        if not self._data_folders:
            raise RuntimeError("Data folder not set. Please call add_data_folder() or set_data_folders() first.")

        if well_name in self._cache:
            self._cache.move_to_end(well_name)
            return self._cache[well_name]

        for folder in self._data_folders:
            file_path = os.path.join(folder, f"{well_name}_data.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)

                if len(self._cache) >= self._max_cache_size:
                    self._cache.popitem(last=False)

                self._cache[well_name] = data
                return data

        raise KeyError(f"Well '{well_name}' not found in any of the data folders.")

    def __contains__(self, well_name):
        if well_name in self._cache:
            return True

        for folder in self._data_folders:
            file_path = os.path.join(folder, f"{well_name}_data.json")
            if os.path.exists(file_path):
                return True
        return False

    def clear_cache(self):
        self._cache.clear()

    @property
    def data_folders(self):
        return self._data_folders

    @property
    def cached_wells(self):
        return list(self._cache.keys())

    @property
    def wells(self):
        """ Returns a list of all available well names from the data folders.
        """
        well_names = set()
        for folder in self._data_folders:
            for filename in os.listdir(folder):
                if filename.endswith('_data.json'):
                    well_name = filename[:-len('_data.json')]
                    well_names.add(well_name)
        return sorted(list(well_names))


# Singleton instance
data_json = DataJSON()
