from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, ClassVar
from pydantic import BaseModel, Field, PrivateAttr
import json
from pathlib import Path

# Define the path to the data directory relative to this file
DATA_DIR = Path(__file__).parent / "data"

class DivisionType(str, Enum):
    TINH = "tinh"
    THANH_PHO = "thanh-pho"
    QUAN = "quan"
    HUYEN = "huyen"
    THI_XA = "thi-xa"
    PHUONG = "phuong"
    XA = "xa"
    THI_TRAN = "thi-tran"

class AdministrativeUnit(BaseModel):
    name: str
    slug: str
    type: DivisionType
    name_with_type: str
    code: str
    parent_code: Optional[str] = None
    path: Optional[str] = None
    path_with_type: Optional[str] = None

class Ward(AdministrativeUnit):
    pass

class District(AdministrativeUnit):
    _wards_cache: Optional[List[Ward]] = PrivateAttr(default=None)

    @property
    def wards(self) -> List[Ward]:
        """Get wards for this district. Loaded from cache or disk."""
        if self._wards_cache is not None:
            return self._wards_cache

        # Try to load from file
        file_path = DATA_DIR / "xa_phuong" / f"{self.code}.json"
        if not file_path.exists():
             self._wards_cache = []
             return []
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._wards_cache = [Ward(**item) for item in data.values()]
        return self._wards_cache

class Province(AdministrativeUnit):
    _districts_cache: Optional[List[District]] = PrivateAttr(default=None)

    @property
    def districts(self) -> List[District]:
        """Get districts for this province. Loaded from cache or disk."""
        if self._districts_cache is not None:
            return self._districts_cache

        file_path = DATA_DIR / "quan_huyen" / f"{self.code}.json"
        if not file_path.exists():
            self._districts_cache = []
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self._districts_cache = [District(**item) for item in data.values()]
        return self._districts_cache

    @classmethod
    def all(cls) -> List[Province]:
        """Get all provinces (Cached)."""
        return DivisionRegistry.get_all_provinces()

    @classmethod
    def get(cls, code: str) -> Optional[Province]:
        """Get a province by code (Cached)."""
        return DivisionRegistry.get_province_by_code(code)
    
    @classmethod
    def search(cls, query: str) -> List[Province]:
        """Search provinces by name or slug (accent-insensitive)."""
        import text_unidecode
        
        queryset = cls.all()
        query = text_unidecode.unidecode(query).lower().strip()
        
        return [
            p for p in queryset 
            if query in text_unidecode.unidecode(p.name).lower() or query in p.slug.replace("-", " ")
        ]

class DivisionRegistry:
    """
    Singleton registry to manage administrative data.
    Handles caching and lazy loading of global data.
    """
    _provinces: ClassVar[Optional[List[Province]]] = None
    _provinces_map: ClassVar[Optional[Dict[str, Province]]] = None

    @classmethod
    def load_provinces(cls):
        """Loads provinces from disk if not already loaded."""
        if cls._provinces is not None:
            return

        file_path = DATA_DIR / "tinh_tp.json"
        if not file_path.exists():
            cls._provinces = []
            cls._provinces_map = {}
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Load and sort by code
        provinces_list = [Province(**item) for item in data.values()]
        cls._provinces = sorted(provinces_list, key=lambda p: p.code)
        
        # Build index
        cls._provinces_map = {p.code: p for p in cls._provinces}

    @classmethod
    def get_all_provinces(cls) -> List[Province]:
        cls.load_provinces()
        return cls._provinces # type: ignore

    @classmethod
    def get_province_by_code(cls, code: str) -> Optional[Province]:
        cls.load_provinces()
        return cls._provinces_map.get(code) # type: ignore
