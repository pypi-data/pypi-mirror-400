# libcgipy

## インストール方法
```bash  
pip install libcgipy
```

## 使い方

- 旧モジュール  
```python
import cgi
```

- 新モジュール  
```python
import pycgi
```

---

- 旧モジュール  
```python
import cgitb
```

- 新モジュール  
```python
import pycgitb
```

---

### 簡易CGIサーバの立ち上げ

```python
from httpcgi import CGIHTTP

if __name__ == "__main__":
    CGIHTTP("0.0.0.0", 8000).serve_forever()
```