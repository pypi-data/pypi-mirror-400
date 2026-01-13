from ...core.errors import ValidationError


def ensure_scalar(value):
    if isinstance(value, (dict, list)):
        raise ValidationError("expected scalar")
