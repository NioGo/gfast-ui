from pathlib import Path
import re
root = Path('src')
no_border = []
resizable_missing = []
for path in root.rglob('*.vue'):
    text = path.read_text('utf-8')
    # match actual <el-table> tags but not <el-table-column>
    for m in re.finditer(r'<el-table(?!-column)([^>]*)>', text):
        tag = m.group(0)
        if re.search(r'\bborder\b', tag) is None:
            no_border.append((path, tag.strip().replace('\n', ' ')))
    for m in re.finditer(r'<el-table-column([^>]*)>', text):
        attrs = m.group(1)
        if re.search(r'\bresizable\b', attrs) is None:
            resizable_missing.append((path, m.group(0).strip().replace('\n', ' ')))
print('tables without border:', len(no_border))
for path, tag in no_border[:20]:
    print(path, tag)
print('columns without resizable:', len(resizable_missing))
for path, tag in resizable_missing[:20]:
    print(path, tag)
