import hashlib
import shutil
import dataclasses
from pathlib import Path

LOGGER_FORMAT = '%(asctime)s| %(message)s'

def get_hash(text: str) -> int:
    hash_obj = hashlib.md5(text.encode('utf-8'))
    hash_bytes = hash_obj.digest()[:8]
    hash_id = int.from_bytes(hash_bytes, byteorder='big', signed=False)
    return hash_id

@dataclasses.dataclass
class Config:
    module_names: list[str]
    open_api_key: str
    work_dir: Path

    @property
    def chunk_dir(self):
        return self.work_dir / 'chunks'
    
    @property
    def runtime_dir(self):
        return self.work_dir / 'runtime'
    
    @property
    def sql_log_file(self):
        return self.runtime_dir / 'sql.log'
    
    @property
    def stack_trace_log_file(self):
        return self.runtime_dir / 'stack_trace.log'
    

def rm_dir(dir: Path):
    if dir.exists():
        shutil.rmtree(dir)
    dir.mkdir(parents=True, exist_ok=True)


def load_config(config: dict):
    return Config(
        module_names=config['MODULE_PATH'],
        open_api_key=config['OPENAI_API_KEY'],
        work_dir=Path(config['WORKDIR']),
    )