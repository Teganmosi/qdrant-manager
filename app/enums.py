from enum import Enum

class RoleEnum(str, Enum):
    """Enum for user roles, ensuring type-safe role assignments."""
    ADMIN = "ADMIN"
    VIEWER = "VIEWER"

class DistanceEnum(str, Enum):
    """Enum for Qdrant distance metrics."""
    COSINE = "Cosine"
    DOT = "Dot"
    EUCLID = "Euclid"
    MANHATTAN = "Manhattan"