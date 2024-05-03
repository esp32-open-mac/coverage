import sys
import datetime

branchname = sys.argv[1]
commit = sys.argv[2]
date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")

replacements = {
    'BRANCH': branchname,
    'COMMIT': commit,
    'DATE': date
}

with open('branch_index.html') as html_template:
    content = html_template.read()
    for key, value in replacements.items():
        content = content.replace(f'${key}', value)

with open(f'output/branches/{branchname}/index.html', 'w') as outfile:
    outfile.write(content)