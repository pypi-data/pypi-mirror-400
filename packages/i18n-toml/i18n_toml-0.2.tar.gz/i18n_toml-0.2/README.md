# i18n-toml

![Python Version](https://badgen.net/pypi/python/i18n-toml)
![Package Version](https://badgen.net/pypi/v/i18n-toml)

Internationalization support library for Python projects.
It expects a **toml** file format to parse localized strings hierarchically.

The library requires a Python language version >= 3.11, as it uses the built-in `tomllib` library.
___

## Installation

Install with `pip`:
```sh
pip install i18n-toml
```

Install with `uv`:
```sh
uv add i18n-toml
```

## Folder Structure

The library expects the folder structure for localization toml-files:

```
localizations/
└── locale_index/
    └── content_file.toml
```

For example, the structure of localizations of messages and button captions for Russian, English and Spanish locales could be:

```
localizations_folder/
├── en/
│   ├── messages.toml
│   └── buttons.toml
├── es/
│   ├── messages.toml
│   └── buttons.toml
└── ru/
    ├── messages.toml
    └── buttons.toml
```

## Locale file structure

The standard toml format can be used in each locale file, including sections and dot-separated keys.

Example of locale file:

**`buttons.toml`**
```toml
# locales/en/buttons.toml
[auth]
login_btn = "Login"
logout_btn = "Logout"
[common]
ok_btn = "Ok"
cancel_btn = "Cancel"
```


## Usage

Import the library:
```python
import i18n_toml
```

Create **`I18nToml`** object, passing the localizations folder path and locale index to use:

```python
from pathlib import Path

i18n = I18nToml(Path('./locales'), 'en')
```
_**Warning:**_ _the locale index is case sensitive!_

Use `get` method of the object to obtain text value by key passed.
The key is dot-separated string representing path to the value needed, starting by file name and navigating futher inside the file hierarchy (sections, keys).

```python
caption = i18n.get("buttons.common.ok_btn")
```
**Output:** `"Ok"`

It's possible to use object's functor call, that is similar to using `get` method:

```python
caption = i18n("buttons.common.ok_btn")
```

*Added in version 0.2*

The `get` method supports additional `**kwargs` arguments to set values for `{...}` placeholders in string values.
For example, the string in toml file:

```toml
welcome = "Welcome, {username}!"
```

can be obtained with user name substituted by call:

```python
msg = i18n("welcome", username="John")
```
**Output:** `"Welcome, John!"`

## Dependencies

The library has no external dependencies, using only standard language tools.
However, a Python version of at least **3.11** is required, since the `tomllib` library is used to work with toml files, which is built into the language starting with the specified version.
