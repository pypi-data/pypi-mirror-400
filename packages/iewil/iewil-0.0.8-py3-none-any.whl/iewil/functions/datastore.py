import os
import json
from .display import Display

class DataStore:
    folder = "cache"
    filename = "data.json"

    @classmethod
    def _file_path(cls):
        os.makedirs(cls.folder, exist_ok=True)
        return os.path.join(cls.folder, cls.filename)

    @classmethod
    def _load(cls):
        file = cls._file_path()
        if os.path.exists(file):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                    return data
            except json.JSONDecodeError:
                return {}
        return {}

    @classmethod
    def _save(cls, data):
        with open(cls._file_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @classmethod
    def simpan(cls, key: str, value: str = None) -> str:
        """
        Simpan key-value.
        - Jika value diberikan, langsung simpan
        - Jika value None, minta input user
        """
        data = cls._load()
        if key in data:
            return data[key]

        if value is None:
            Display.isi(key)
            value = input().strip()

        data[key] = value
        cls._save(data)
        print(f"{key} berhasil disimpan\n")
        return value

    @classmethod
    def hapus(cls, key: str) -> bool:
        """Hapus key dari data, return True jika berhasil"""
        data = cls._load()
        if key not in data:
            return False
        del data[key]
        cls._save(data)
        print(f"{key} berhasil dihapus\n")
        return True
