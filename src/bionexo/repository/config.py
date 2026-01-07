from pydantic import BaseModel

from bionexo.application.definitions import Environment

class RepositoryConfig(BaseModel):
    environment: Environment