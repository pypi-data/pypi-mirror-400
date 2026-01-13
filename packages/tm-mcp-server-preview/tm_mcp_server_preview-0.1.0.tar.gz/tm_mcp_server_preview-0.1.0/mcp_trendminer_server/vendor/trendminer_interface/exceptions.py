class ResourceNotFound(Exception):
    """Resource does not exist or is not accessible to the current user"""


class AmbiguousResource(Exception):
    """Two or more equally valid resources exist for given reference"""

class VersionMismatchWarning(UserWarning):
    """SDK version does not explicitly support TrendMiner version"""
