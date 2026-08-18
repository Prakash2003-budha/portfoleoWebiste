#!/usr/bin/env python3
import os
import sys

em_dash = ''
removed = 0
fixed = 0

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if '.venv' not in d.lower()]
    for f in files:
        if f.endswith(('.py', '.html', '.css', '.js', '.env', '.env.example', '.sql')):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                c = content.count(em_dash)
                if c > 0:
                    new = content.replace(em_dash, '')
                    with open(fp, 'w', encoding='utf-8') as fh:
                        fh.write(new)
                    removed += c
                    fixed += 1
                    print(f'  {fp}: {c} em-dashes removed')
            except Exception as e:
                print(f'  ERROR {fp}: {e}')

print(f'\nTotal files fixed: {fixed}')
print(f'Total em-dashes removed: {removed}')