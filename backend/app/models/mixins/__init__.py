# app/models/mixins/__init__.py
# Expose ActorMixin at package-level for compatibility with different import styles.

from .actor_mixin import ActorMixin

__all__ = [
    "ActorMixin",
]
