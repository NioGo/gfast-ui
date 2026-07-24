from pathlib import Path
import re
root = Path('src')
missing_border = 0
missing_resizable = 0
for path in root.rglob('*.vue'):
    text = path.read_text('utf-8')
    original = text

    def add_border(match):
        global missing_border
        tag = match.group(0)
        attrs = match.group(1)
        if re.search(r'\bborder\b', attrs):
            return tag
        missing_border += 1
        return f'<el-table border{attrs}>'

    def add_resizable(match):
        global missing_resizable
        tag = match.group(0)
        attrs = match.group(1)
        if re.search(r'\bresizable\b', attrs):
            return tag
        missing_resizable += 1
        return f'<el-table-column resizable{attrs}>'

    text = re.sub(r'<el-table(?!-column)(\b[^>]*)>', add_border, text)
    text = re.sub(r'<el-table-column(\b[^>]*)>', add_resizable, text)

    if text != original:
        path.write_text(text, 'utf-8')

print(f'tables missing border fixed: {missing_border}')
print(f'columns missing resizable fixed: {missing_resizable}')
