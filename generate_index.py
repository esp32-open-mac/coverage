import sys

print(sys.argv[1])
all_branches = sys.argv[1].strip(':').split(':')
print(all_branches)

html = ''
for branch in all_branches:
    html += f'<li><a href="./branches/{branch}">{branch}</a></li>\n'

with open('global_index.html') as infile:
    content = infile.read()
    content = content.replace('$LIST', html)

with open("output/index.html", 'w') as outfile:
    outfile.write(content)