# hanhchinhvn

A modern, professional Python library for accessing Vietnam's administrative divisions (Provinces, Districts, Wards).

## Installation

```bash
pip install hanhchinhvn
```

## Usage

```python
from hanhchinhvn import Province, District, Ward

# Get all provinces
provinces = Province.all()
for p in provinces:
    print(p.name)

# Get specific province by code
hanoi = Province.get("01")
print(hanoi.name)

# Get districts
districts = hanoi.districts
```
