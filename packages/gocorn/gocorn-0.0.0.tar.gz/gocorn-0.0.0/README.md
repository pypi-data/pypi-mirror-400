<p align="center">
  <img src="examples/Gophercorn.png" width="auto" height="100" alt="Siberia" />
</p>

# Gophercorn
Fast Python ASGI server written in Go. 

Work in progress, call back soon...

### Install
```bash
pip install gophercorn
```

### Setup

```python
from flask import Flask  # Or any other ASGI application framework
from gocorn import Gophercorn

flask_app = Flask(__name__)

if __name__ == "__main__":
    gocorn = Gophercorn(wsgi_application=flask_app)
    gocorn.serve() 
```