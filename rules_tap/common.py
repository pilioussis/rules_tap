import hashlib
import shutil
import dataclasses
from pathlib import Path

LOGGER_FORMAT = '%(asctime)s| %(message)s'

def get_hash(text: str) -> int:
    hash_obj = hashlib.md5(text.encode('utf-8'))
    hash_bytes = hash_obj.digest()[:8]
    hash_id = int.from_bytes(hash_bytes, byteorder='big', signed=False)
    return hash_id >> 1 # shift right to avoid overflow due to unsigned

@dataclasses.dataclass
class ContextConfig:
    module_names: list[str]
    file_chunk_exclude_paths: list[str]
    open_api_key: str
    work_dir: Path

    @property
    def chunk_dir(self):
        return self.work_dir / 'chunks'

    @property
    def code_dir(self):
        return self.chunk_dir / 'code'
    
    @property
    def runtime_dir(self):
        return self.work_dir / 'runtime'
    
    @property
    def sql_log_file(self):
        return self.runtime_dir / 'sql.log'
    
    @property
    def stack_trace_log_file(self):
        return self.runtime_dir / 'stack_trace.log'
    
    @property
    def vector_index_file(self):
        return self.work_dir / 'vector_index.faiss'

    @property
    def id_to_text_file(self):
        return self.work_dir / 'id_to_text.json'
    

def rm_dir(dir: Path):
    if dir.exists():
        shutil.rmtree(dir)
    dir.mkdir(parents=True, exist_ok=True)


def load_config(config: dict):
    return ContextConfig(
        module_names=config['MODULE_PATHS'],
        open_api_key=config['OPENAI_API_KEY'],
        work_dir=Path(config['WORKDIR']),
        file_chunk_exclude_paths=config['FILE_CHUNK_EXCLUDE_PATHS'],
    )