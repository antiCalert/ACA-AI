# qgen/dataset_types.py
from .schemas import TextRecord

def row_to_textrecord(row: dict) -> TextRecord:
    return TextRecord(
        text=row["text"],
        source=row["source"],
        title=row["title"],
        line_number=int(row["line_number"]),
    )
