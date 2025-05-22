from cscs_tools.version.repositories.version_file_repository import VersionFileRepository


class VersionService:
    def __init__(self, file=None):
        self.file_repo = VersionFileRepository(file)

    def get_version(self):
        return self.file_repo.get_version()

    def set_version(self, version):
        return self.file_repo.save(version)
