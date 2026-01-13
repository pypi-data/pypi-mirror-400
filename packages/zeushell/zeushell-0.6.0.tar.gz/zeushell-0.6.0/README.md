# zeushell

A simple interactive action-shell framework.  
Write functions — run them as shell commands.

## Features

- Function-based command system
- Interactive shell runtime
- Customizable shell prompt
- Safe function registry
## Install

```bash
pip install zeushell
```

## Quick Start

```python
from zeushell import function, name, run

@function()
def hi(user):
    return f"Hello {user}"

name("zeushell")
run()
```

Shell:

```
zeushell: hi Tom
hi Tom
```

## License

MIT
