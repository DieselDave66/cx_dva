from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    databricks_warehouse_id: Optional[str] = Field(
        default=None,
        description="The ID of the Databricks SQL warehouse to connect to",
    )

    default_limit: int = Field(
        default=100,
        description="Default number of records to return in paginated responses",
    )

    max_limit: int = Field(
        default=200,
        description="Maximum number of records that can be returned in a single request",
    )

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "allow",
    }

settings = Settings()

def get_settings() -> Settings:
    return settings