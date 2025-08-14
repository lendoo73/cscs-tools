from cscs_tools.version.services.version_service import VersionService

service = VersionService()
version = service.get_version() # Reads from /version.json by default

print(version.str_repr())

service = VersionService("sample/version/my_version.txt")
version = service.get_version()

print(version.str_repr())