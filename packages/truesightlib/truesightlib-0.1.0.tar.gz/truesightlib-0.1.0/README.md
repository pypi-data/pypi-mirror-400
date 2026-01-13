# TRUESIGHT LIB

### Instalação

```bash

pip install truesightlib # ou
uv add truesightlib
```


### Modo de usar

```python

from truesight import Consumer, Loader

data = """
    [INFO] 2026-01-03: TESTEEEEEEEE
    [INFO] 2026-01-03: TESTEEEEEEEE
    [INFO] 2026-01-03: TESTEEEEEEEE
    [INFO] 2026-01-03: TESTEEEEEEEE
    [INFO] 2026-01-03: TESTEEEEEEEE
    [INFO] 2026-01-03: TESTEEEEEEEE
    [INFO] 2026-01-03: TESTEEEEEEEE
"""


def main():
    loader = Loader()
    send = loader.config(data=data)
    print(send)
    

if __name__ == "__main__":
    main()
```