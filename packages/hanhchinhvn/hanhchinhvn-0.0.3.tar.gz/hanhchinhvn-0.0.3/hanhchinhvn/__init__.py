import os
import glob
import json
from typing import Generator, Tuple, Optional, NamedTuple

from .models import DivisionType, Province, District, Ward, DivisionRegistry

# Path to data directory
_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def iter_all_provinces() -> Generator[Province, None, None]:
    """
    Trả về generator duyệt qua tất cả tỉnh thành.
    
    Yields:
        Province: Đối tượng Province cho mỗi tỉnh/thành phố.
    
    Example:
        >>> for province in iter_all_provinces():
        ...     print(province.name)
    """
    for province in DivisionRegistry.get_all_provinces():
        yield province


def iter_all_districts() -> Generator[Tuple[str, District], None, None]:
    """
    Trả về generator duyệt qua tất cả quận huyện của TOÀN BỘ cả nước.
    
    Yields:
        Tuple[str, District]: Tuple gồm (mã_tỉnh_cha, District_Object)
    
    Example:
        >>> for province_code, district in iter_all_districts():
        ...     print(f"{province_code}: {district.name}")
    """
    data_dir = os.path.join(_DATA_DIR, "quan_huyen")
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    for file_path in sorted(json_files):
        # Lấy mã tỉnh từ tên file (vd: 01.json -> 01)
        province_code = os.path.splitext(os.path.basename(file_path))[0]
        
        with open(file_path, "r", encoding="utf-8") as f:
            districts_data = json.load(f)
            for d_data in districts_data.values():
                yield province_code, District(**d_data)


def iter_all_wards() -> Generator[Tuple[str, Ward], None, None]:
    """
    Trả về generator duyệt qua tất cả xã phường.
    
    Yields:
        Tuple[str, Ward]: Tuple gồm (mã_huyện_cha, Ward_Object)
    
    Example:
        >>> for district_code, ward in iter_all_wards():
        ...     print(f"{district_code}: {ward.name}")
    """
    data_dir = os.path.join(_DATA_DIR, "xa_phuong")
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    for file_path in sorted(json_files):
        # Lấy mã huyện từ tên file (vd: 001.json -> 001)
        district_code = os.path.splitext(os.path.basename(file_path))[0]
        
        with open(file_path, "r", encoding="utf-8") as f:
            wards_data = json.load(f)
            for w_data in wards_data.values():
                yield district_code, Ward(**w_data)


# ============================================================================
# Reverse Lookup Functions
# ============================================================================

def get_district_by_code(district_code: str) -> Optional[District]:
    """
    Tìm quận/huyện theo mã.
    
    Args:
        district_code: Mã quận/huyện (vd: "001", "760")
    
    Returns:
        District object hoặc None nếu không tìm thấy.
    """
    # District code có dạng "XXX" - 3 chữ số
    # Province code là 2 ký tự đầu của parent_code hoặc phải tìm trong file
    data_dir = os.path.join(_DATA_DIR, "quan_huyen")
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            districts_data = json.load(f)
            if district_code in districts_data:
                return District(**districts_data[district_code])
    return None


def get_ward_by_code(ward_code: str) -> Optional[Ward]:
    """
    Tìm xã/phường theo mã.
    
    Args:
        ward_code: Mã xã/phường (vd: "00001", "26734")
    
    Returns:
        Ward object hoặc None nếu không tìm thấy.
    """
    data_dir = os.path.join(_DATA_DIR, "xa_phuong")
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            wards_data = json.load(f)
            if ward_code in wards_data:
                return Ward(**wards_data[ward_code])
    return None


class FullAddress(NamedTuple):
    """Full address with ward, district and province info."""
    ward: Ward
    district: District
    province: Province
    full_address: str  # "Phường X, Quận Y, Tỉnh Z"


def get_full_address_by_ward_code(ward_code: str) -> Optional[FullAddress]:
    """
    Trả về địa chỉ đầy đủ từ mã phường/xã.
    
    Hữu ích khi cần tính phí ship vùng miền từ mã phường trong đơn hàng cũ.
    
    Args:
        ward_code: Mã xã/phường (vd: "00001")
    
    Returns:
        FullAddress(ward, district, province, full_address) hoặc None.
    
    Example:
        >>> result = get_full_address_by_ward_code("00001")
        >>> if result:
        ...     print(result.full_address)  # "Phường Phúc Xá, Quận Ba Đình, Thành phố Hà Nội"
        ...     print(result.province.code)  # "01"
    """
    # Tìm file chứa ward
    data_dir = os.path.join(_DATA_DIR, "xa_phuong")
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            wards_data = json.load(f)
            if ward_code in wards_data:
                ward = Ward(**wards_data[ward_code])
                district_code = os.path.splitext(os.path.basename(file_path))[0]
                
                # Tìm district
                district = get_district_by_code(district_code)
                if not district:
                    return None
                
                # Tìm province từ parent_code của district
                province = DivisionRegistry.get_province_by_code(district.parent_code or "")
                if not province:
                    return None
                
                full_addr = f"{ward.name_with_type}, {district.name_with_type}, {province.name_with_type}"
                return FullAddress(
                    ward=ward,
                    district=district,
                    province=province,
                    full_address=full_addr
                )
    return None


__all__ = [
    # Models
    "DivisionType",
    "Province", 
    "District",
    "Ward",
    "FullAddress",
    # Generator functions
    "iter_all_provinces",
    "iter_all_districts", 
    "iter_all_wards",
    # Lookup functions
    "get_district_by_code",
    "get_ward_by_code",
    "get_full_address_by_ward_code",
]

