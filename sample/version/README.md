# Version

## 🚀 Usage

Place a `version.json` in your project root:

```json
{
  "major": 0,
  "minor": 2,
  "patch": 1,
  "inherit": true
}
```

Then use it like this:

```python
from cscs.version.services.version_service import VersionService

service = VersionService()  # Automatically finds version.json upwards
version = service.get_version()
print(version.str_repr())
```

Or specify the file path manually:

```python
service = VersionService(file="path/to/my_ver.custom")
```

## 🧱 JSON Structure

The required structure of the `version.json` file is:

```json
{
  "major": 0,
  "minor": 2,
  "patch": 1,
  "inherit": true
}
```