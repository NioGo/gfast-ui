from pathlib import Path
import re
root = Path('src')
el_table_re = re.compile(r'(<el-table\b)([^>]*)(>)', re.I | re.S)
show_count = 0
for path in root.rglob('*.vue'):
    content = path.read_text(encoding='utf-8')
    def repl(m):
        global show_count
        tag_start, attrs, tag_end = m.groups()
        if re.search(r'(?<![:\w])(?:border|:border|v-bind:border)(?![\w-])', attrs, re.I):
            return m.group(0)
        show_count += 1
        return f"{tag_start} border{attrs}{tag_end}"
    new_content = el_table_re.sub(repl, content)
    if new_content != content:
        path.write_text(new_content, encoding='utf-8')
print(f"Updated {show_count} el-table tags")
