<p align="center">
  <img src="examples/logo.png" width="200" height="200" alt="Siberia" />
</p>

# Gofercorn
Fast Python ASGI server written in Go.

### Install
```bash
pip install gofercorn
```

### Setup

```python
from flask import Flask  # Or any other WSGI application framework
from volk import Volk

flask_app = Flask(__name__)

if __name__ == "__main__":
    volk = Volk(wsgi_application=flask_app)
    volk.serve() 
```