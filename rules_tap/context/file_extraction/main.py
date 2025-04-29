from contextlib import ExitStack
from rules_tap.common import ContextConfig, get_hash, rm_dir
from pathlib import Path
import fnmatch

GLOBAL_EXCLUDE_FILES = [
	'**/*.pyc',
]

def get_file_paths(config: ContextConfig, module_path: str):
	exclude = GLOBAL_EXCLUDE_FILES + config.file_chunk_exclude_paths
	files = []
	root = Path(module_path)
	if not root.exists():
		raise Exception(f"Module path {module_path} does not exist")
	for f in root.rglob('*.py'):
		if f.is_file():
			file_str = str(f)
			if any(fnmatch.fnmatch(file_str, pattern) for pattern in exclude):
				continue
			files.append(file_str)
	return files

def file_extraction(config: ContextConfig):
	code_dir = config.chunk_dir / "code"
	rm_dir(code_dir)
	for module in config.module_names:
		file_paths = get_file_paths(config, module)

		for file_path in file_paths:
			file_path = Path(file_path)
			# read original file content
			content = file_path.open('r', encoding='utf-8').read().strip()
			out_file_path = file_path.relative_to(module)
			# compute hash id for filename
			chunk_file = code_dir / out_file_path
			# create directory for chunk_file if it does not exist
			chunk_file.parent.mkdir(parents=True, exist_ok=True)
			# write content to new chunk file
			chunk_file.open('w', encoding='utf-8').write(content)

# def file_extraction(config: ContextConfig):
# 	docs = []

# 	for module in config.module_names:
# 		for filepath in get_file_paths(config, module):
# 			with open(filepath, 'r', encoding='utf-8') as f:
# 				code = f.read()
# 				# Store file path as metadata (useful for retrieval context)
# 				docs.append({"text": code, "metadata": {"source": filepath}})

# 	# Set up a text splitter for Python code
# 	splitter = RecursiveCharacterTextSplitter.from_language(
# 		language="python", chunk_size=2000, chunk_overlap=200
# 	)
# 	all_chunks = []
# 	for d in docs:
# 		chunks = splitter.split_text(d["text"])
# 		print("----------------------------------------------------------------------------------")
# 		print("----------------------------------------------------------------------------------")
# 		print("----------------------------------------------------------------------------------")
# 		print("----------------------------------------------------------------------------------")
# 		print("----------------------------------------------------------------------------------")
# 		print(d["metadata"])
# 		print(f"Total chunks: {len(chunks)}")
# 		for c in chunks:
# 			hash_id = get_hash(c)
# 			chunk_file = config.chunk_dir / f"code_{hash_id}.chunk"
# 			# create directory for chunk_file if it does not exist
# 			chunk_file.parent.mkdir(parents=True, exist_ok=True)
# 			# write content to new chunk file
# 			chunk_file.open('w', encoding='utf-8').write(c)

# 			print(c)
# 			print("----------------------------------------------------------------------------------")

# 		# Each element in chunks is a dict with 'text' and 'metadata'
# 		all_chunks.extend(chunks)
# 	return all_chunks