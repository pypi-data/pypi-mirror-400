class ArtifactStoreError(Exception):
    pass


class NotFoundError(ArtifactStoreError):
    pass


class StorageFullError(ArtifactStoreError):
    pass


class InvalidArtifactIdError(ArtifactStoreError):
    pass
