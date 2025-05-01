import dataclasses
from pathlib import Path

@dataclasses.dataclass
class EmbeddingConfig:
    work_dir: Path
    chunk_size: int = 1000
    chunk_overlap: int = 200
    model: str = "text-embedding-3-large"
    transpose_sql_schema_token: str ='ai_sandbox'

    @property
    def chunk_dir(self):
        return self.work_dir / 'chunks'
    
    @property
    def schema_file(self):
        return self.chunk_dir / 'schema.sql'

    @property
    def code_dir(self):
        return self.chunk_dir / 'code'
    
    @property
    def vector_index_file(self):
        return self.work_dir / 'vector_index'

    @property
    def id_to_text_file(self):
        return self.work_dir / 'id_to_text.json'


def load_config():
    return EmbeddingConfig(
        work_dir=Path('/app/data'),
    )