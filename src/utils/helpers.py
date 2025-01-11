import uuid

def generate_unique_filename(extension: str) -> str:
    return f"{uuid.uuid4()}.{extension}"
