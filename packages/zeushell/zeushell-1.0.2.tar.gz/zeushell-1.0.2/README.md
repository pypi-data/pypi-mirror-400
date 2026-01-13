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
from zeushell import Zeushell

z = Zeushell()
@z.function()
def hi(user):
    return "Hello "+user

z.name("zeushell")
z.run()
```

Shell:

```
zeushell: hi Tom
hi Tom
```

## License

MIT
