import uuid


def generate_unique_column_name(existing_columns: set[str], prefix: str = "temp_col") -> str:
    """Generate a unique column name that doesn't conflict with existing columns."""
    base_name = f"{prefix}_{uuid.uuid4().hex[:8]}"
    while base_name in existing_columns:
        base_name = f"{prefix}_{uuid.uuid4().hex[:8]}"
    return base_name
