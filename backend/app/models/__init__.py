# app/models/__init__.py
"""
Canonical models package. Re-exports the Declarative Base and model classes.
This module intentionally imports model modules so they register with the single
Declarative Base defined in app.db.base.
"""
from typing import Any


# Import the canonical Base from the db package
from ..db.base import Base # type: ignore


# Import enums early so code can reference them from models
from . import enums as _enums # noqa: E402


# Import model modules so SQLAlchemy tables register with Base.metadata.
# Import the modules (not direct class names) to minimize circular import issues.
from . import user as _user # noqa: E402
from . import blocks as _blocks # noqa: E402
from . import fruit as _fruit # noqa: E402
from . import intake as _intake # noqa: E402
from . import lab as _lab # noqa: E402
from . import audit as _audit # noqa: E402


# Expose the primary classes at package level for convenience
User = getattr(_user, "User", None)
Block = getattr(_blocks, "Block", None)
BlockSubdivision = getattr(_blocks, "BlockSubdivision", None)
Fruit = getattr(_fruit, "Fruit", None)
Intake = getattr(_intake, "Intake", None)
IntakeComponent = getattr(_intake, "IntakeComponent", None)
Addition = getattr(_intake, "Addition", None)
LabResult = getattr(_lab, "LabResult", None)
AuditLog = getattr(_audit, "AuditLog", None)
UserRole = getattr(_enums, "UserRole", None)


# Backwards compatibility
FruitIntake = Intake # type: ignore


__all__ = [
"Base",
"User",
"Block",
"BlockSubdivision",
"Fruit",
"Intake",
"IntakeComponent",
"Addition",
"LabResult",
"AuditLog",
"UserRole",
"FruitIntake",
]