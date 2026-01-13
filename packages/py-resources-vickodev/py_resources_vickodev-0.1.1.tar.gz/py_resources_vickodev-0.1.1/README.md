# py-resources

A lightweight and type-safe internationalization (i18n) library for Python applications. Manage multilingual messages with ease using a simple dictionary-based approach.

## Features

- 🌍 **Simple Dictionary-Based**: No complex configuration files, just Python dictionaries
- 🔒 **Type-Safe**: Full support for static typing with TypeVar and Generics
- 🎯 **Key Validation**: Ensures all keys exist in all languages at initialization
- 🔄 **Runtime Language Switching**: Change languages dynamically at any time
- 📝 **Parameter Interpolation**: Support for template variables using `{{variable}}` syntax
- 🚀 **Zero Dependencies**: Pure Python, no external packages required
- ⚡ **Lightweight**: Minimal overhead, perfect for any Python application

## Installation

Install from test.pypi.org:

```bash
pip install -i https://test.pypi.org/simple/ py-resources-vickodev
```

## Quick Start

### 1. Define Your Messages

Create separate files for each language:

**en.py** (English):
```python
en_messages = {
    "WELCOME": "Welcome to our application!",
    "USER_NOT_FOUND": "User with id '{{id}}' not found",
    "ERROR_MESSAGE": "An error occurred: {{error}}",
}
```

**es.py** (Spanish):
```python
es_messages = {
    "WELCOME": "¡Bienvenido a nuestra aplicación!",
    "USER_NOT_FOUND": "Usuario con id '{{id}}' no encontrado",
    "ERROR_MESSAGE": "Ocurrió un error: {{error}}",
}
```

### 2. Define Message Keys

Create an enum for your message keys:

**keys.py**:
```python
class MessageKeys:
    WELCOME = "WELCOME"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    ERROR_MESSAGE = "ERROR_MESSAGE"

    @classmethod
    def as_dict(cls):
        return {k: v for k, v in vars(cls).items() if not k.startswith('_')}
```

### 3. Initialize Resources

**__init__.py**:
```python
from py_resources_vickodev import Resources
from keys import MessageKeys
from en import en_messages
from es import es_messages

# Create the resources instance
resources = Resources(
    locals={"en": en_messages, "es": es_messages},
    local_keys=MessageKeys.as_dict(),
    default_language="en",
)

__all__ = ["resources", "Resources", "MessageKeys"]
```

### 4. Use in Your Application

```python
from domain.locals.messages import resources, MessageKeys

# Set the current language
resources.init("es")

# Get a simple message
message = resources.get(MessageKeys.WELCOME)
print(message)  # "¡Bienvenido a nuestra aplicación!"

# Get a message with parameters
message = resources.get_with_params(
    MessageKeys.USER_NOT_FOUND,
    {"id": "12345"}
)
print(message)  # "Usuario con id '12345' no encontrado"

# Get a message in a specific language
message = resources.get(MessageKeys.WELCOME, language="en")
print(message)  # "Welcome to our application!"
```

## API Reference

### Constructor

```python
Resources(
    locals: Dict[str, Dict[str, str]],
    local_keys: Dict[str, str],
    default_language: Optional[str] = None
)
```

**Parameters:**
- `locals`: Dictionary mapping language codes to message dictionaries
- `local_keys`: Dictionary of available message keys
- `default_language`: Fallback language if requested language is not available

**Raises:**
- `ValueError`: If default language not found or if any key is missing in any language

### Methods

#### `set_default_language(language: str) -> None`

Sets the default fallback language.

```python
resources.set_default_language("en")
```

#### `init(language: str) -> None`

Sets the current working language for subsequent calls.

```python
resources.init("es")
```

#### `update_locals(locals: Dict[str, Dict[str, str]], local_keys: Dict[str, str]) -> None`

Updates the message dictionaries at runtime.

```python
resources.update_locals(
    {"en": new_en_messages, "es": new_es_messages},
    new_keys
)
```

#### `get(resource_name: str, language: Optional[str] = None) -> str`

Retrieves a message. Priority order:
1. Specified language
2. Current global language
3. Default language

```python
message = resources.get(MessageKeys.WELCOME)
message = resources.get(MessageKeys.WELCOME, language="en")
```

**Raises:**
- `ValueError`: If resource not found in any language

#### `get_with_params(resource_name: str, params: Dict[str, str], language: Optional[str] = None) -> str`

Retrieves a message and interpolates parameters.

```python
message = resources.get_with_params(
    MessageKeys.USER_NOT_FOUND,
    {"id": "12345"}
)
```

#### `replace_params(text: str, params: Dict[str, str]) -> str` (Static)

Replaces parameters in any string using the `{{variable}}` syntax.

```python
result = Resources.replace_params(
    "Hello {{name}}, you are {{age}} years old",
    {"name": "John", "age": "30"}
)
# "Hello John, you are 30 years old"
```

## Complete Example

```python
from py_resources_vickodev import Resources
from keys import MessageKeys
from messages import resources

# 1. Initialize with Spanish
resources.init("es")

# 2. Get welcome message
welcome = resources.get(MessageKeys.WELCOME)
print(welcome)  # "¡Bienvenido a nuestra aplicación!"

# 3. Handle user not found error
try:
    user_id = "404"
    message = resources.get_with_params(
        MessageKeys.USER_NOT_FOUND,
        {"id": user_id}
    )
    print(message)  # "Usuario con id '404' no encontrado"
except ValueError as e:
    print(f"Error: {e}")

# 4. Switch to English
resources.init("en")
welcome = resources.get(MessageKeys.WELCOME)
print(welcome)  # "Welcome to our application!"

# 5. Get specific language without changing global setting
message = resources.get(MessageKeys.ERROR_MESSAGE, language="es")
print(message)
```

## Advanced Usage

### Multiple Parameter Interpolation

```python
message = resources.get_with_params(
    MessageKeys.ERROR_MESSAGE,
    {
        "error": "Database connection failed",
        "timestamp": "2024-12-27 10:30:00"
    }
)
```

### Error Handling

```python
try:
    message = resources.get("NONEXISTENT_KEY")
except ValueError as e:
    print(f"Message not found: {e}")
    # Fallback to default language
    message = resources.get(MessageKeys.WELCOME, language="en")
```

### Runtime Language Updates

```python
# Update messages at runtime (e.g., from API or database)
new_messages = {
    "en": {"WELCOME": "New welcome message"},
    "es": {"WELCOME": "Nuevo mensaje de bienvenida"}
}

resources.update_locals(
    new_messages,
    MessageKeys.as_dict()
)
```

## Best Practices

1. **Use Enums for Keys**: Always use a keys enum to avoid typos and enable IDE autocomplete
   ```python
   # ✅ Good
   message = resources.get(MessageKeys.WELCOME)
   
   # ❌ Avoid
   message = resources.get("WELCOME")
   ```

2. **Set Default Language Early**: Configure the default language at application startup
   ```python
   resources.set_default_language("en")
   ```

3. **Validate All Languages**: Ensure all keys exist in all languages to catch issues early
   ```python
   # The constructor validates this automatically
   resources = Resources(locals, keys, default_language)
   ```

4. **Use Parameters for Dynamic Content**: Don't concatenate strings, use template variables
   ```python
   # ✅ Good
   message = resources.get_with_params(
       MessageKeys.USER_NOT_FOUND,
       {"id": user_id}
   )
   
   # ❌ Avoid
   message = f"User {user_id} not found"
   ```

5. **Centralize Resource Initialization**: Keep resources in a single module
   ```python
   # domain/locals/messages/__init__.py
   resources = Resources(...)
   
   # Then import from anywhere
   from domain.locals.messages import resources
   ```

## Integration with Frameworks

### Flask

```python
from flask import Flask, request
from py_resources_vickodev import Resources
from domain.locals.messages import resources

default_lang = "en"
resources.init(default_lang)

app = Flask(__name__)

@app.route('/api/users/<user_id>')
def get_user(user_id):
    try:
        lang = request.args.get('lang', 'en')
        user = db.get_user(user_id)
        if not user:
            message = resources.get_with_params(
                MessageKeys.USER_NOT_FOUND,
                {"id": user_id},
                language=lang
            )
            return {"error": message}, 404
    except Exception as e:
        message = resources.get_with_params(
            MessageKeys.ERROR_MESSAGE,
            {"error": str(e)},
            language=lang
        )
        return {"error": message}, 500
```

### FastAPI

```python
from fastapi import FastAPI, Query
from py_resources_vickodev import Resources
from domain.locals.messages import resources

default_lang = "en"
resources.init(default_lang)

app = FastAPI()


@app.get("/api/users/{user_id}")
async def get_user(user_id: str, lang: str = Query("en")):
    user = await db.get_user(user_id)
    if not user:
        message = resources.get_with_params(
            MessageKeys.USER_NOT_FOUND,
            {"id": user_id},
            language=lang
        )
        return {"error": message}
    
    return user
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/harvic3/py-tools/py-resources).
