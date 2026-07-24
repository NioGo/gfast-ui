from pathlib import Path
root = Path('src')
count = 0
for path in root.rglob('*.vue'):
    text = path.read_text('utf-8')
    if 'el-table border-column' in text:
        new = text.replace('el-table border-column', 'el-table-column')
        path.write_text(new, 'utf-8')
        replaced = text.count('el-table border-column')
        count += replaced
        print(f"{path}: replaced {replaced}")
print(f"Total replaced: {count}")
