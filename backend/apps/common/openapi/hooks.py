"""OpenAPI preprocessing hooks."""
from __future__ import annotations


def _endpoint_tags(callback) -> set:
    """Collect tags from class-level + method-level @extend_schema."""
    tags: set = set()
    cls_ann = getattr(callback.cls, "_spectacular_annotation", {})
    tags.update(cls_ann.get("tags", []))
    method_ann = getattr(callback, "_spectacular_annotation", {})
    tags.update(method_ann.get("tags", []))
    return tags


def exclude_internal_endpoints(endpoints, **kwargs):
    """Hide endpoints tagged ``internal`` from the generated schema."""
    filtered = []
    for path, path_regex, method, callback in endpoints:
        if "internal" not in _endpoint_tags(callback):
            filtered.append((path, path_regex, method, callback))
    return filtered