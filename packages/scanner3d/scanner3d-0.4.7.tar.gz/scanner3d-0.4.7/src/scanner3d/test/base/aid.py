from pathlib import Path

def save_settings(obj, folder: Path):
    folder.mkdir(parents=True, exist_ok=True) #TODO how to avoid this check?
    cls_name = obj.__class__.__name__
    snake = ''.join(['_' + c.lower() if c.isupper() else c for c in cls_name]).lstrip('_')
    filename = f"{snake}.txt"

    file = folder / filename
    with open(file, "w", encoding="utf-8") as f:
        f.write(str(obj))
