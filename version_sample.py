from cscs_tools.version.services.version_service import VersionService

service = VersionService("version.json")
version = service.get_version()

print(version.str_repr())
