#!/usr/bin/python

# Usage: generate_listing.py base_dir
import sys, os
if len(sys.argv) != 2:
	print("Usage: generate_listing.py base_dir")
	sys.exit(-1)

def make_tree_file(path):
	name=os.path.basename(path)
	tree = {'name': name}
	is_md5, is_sha1 = name.startswith('md5sum'), name.startswith('sha1sum')
	if is_md5 or is_sha1:
		fd = open(path, 'r')
		tree['contents'] = fd.read().split(None, 1)[0]
		if is_md5: tree['name'] = 'md5'
		if is_sha1: tree['name'] = 'sha1'
		fd.close()
	return tree


def make_tree(path):
	name=os.path.basename(path)
	tree = dict(name=name, children=[], directory=os.path.isdir(path))
	try: lst = os.listdir(path)
	except OSError:
		pass #ignore errors
	else:
		for name in lst:
			if name.startswith('.'): continue
			if name == 'index.html': continue
			fn = os.path.join(path, name)
			if os.path.isdir(fn):
				tree['children'].append(make_tree(fn))
			else:
				tree['children'].append(make_tree_file(fn))
	return tree

def gen_html(tree, depth, parents):
	lines = []
	name = tree.get('name', False)
	fmt_args = {'name': name, 'depth': depth}
	if name:
		if 'contents' in tree:
			fmt_args['contents'] = tree['contents']
			# Show contents directly
			lines.append('<li class="item_{depth}"><div class="txt_{depth}">'.format(**fmt_args))
			lines.append('\t<span class="hash_key">{name}:</span>'.format(**fmt_args))
			lines.append('\t<span class="hash_val">{contents}</span>'.format(**fmt_args))
			lines.append('</div>')
		elif tree.get('directory', False):
			# File
			lines.append('<li class="item_{depth}"><div class="txt_{depth}">{name}</div>'.format(**fmt_args))
		else:
			# Directory
			fmt_args['path'] = '/'.join(parents) + '/' + name
			lines.append('<li class="item_{depth} file"><div class="txt_{depth} file"><a href="{path}">{name}</div></a>'.format(**fmt_args))
	children = tree.get('children', [])
	if children:
		subparents = parents[:]
		if name: subparents.append(name)
		lines.append('<ul>')
		for child in children:
			lines.extend(gen_html(child, depth + 1, subparents))
		lines.append('</ul>')
	if name: lines.append('</li>')
	return ['\t' + line for line in lines]
	

base_dir = sys.argv[1]
contents = ''
tree = make_tree(base_dir)
contents = gen_html(tree, 0, [])

css = """
body {
	background-color: #F0F0FF;
	font-size: 13pt;
}

li {
	list-style-type: none;
}

.item_1 {
	padding-bottom: 10px;
	margin-bottom: 10px;
	font-size: 24pt;
}

.txt_1 {
	padding-bottom: 10px;
	border-bottom: 1px solid #CCC;
}

.txt_2 {
	margin-top: 10px;
	margin-bottom: 5px;
}

.item_2 {
	font-size: 14pt;
}

.item_3 {
	font-size: 14pt;
}

.hash_key {
}

.hash_val {
	font-family: monospace;
	font-size: 10pt;
}
""";

template = """<html><head>
<title>fish files</title>
<style type="text/css">
{css}
</style>
</head><body>
{contents_str}
</body></html>"""

html = template.format(css=css, contents_str='\n'.join(contents))
target_path = os.path.join(base_dir, 'index.html')
fd = open(target_path, 'w')
fd.write(html)
fd.close()
print "Output written to '" + target_path + "'"
