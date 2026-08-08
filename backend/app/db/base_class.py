import re
from typing import Any
from sqlalchemy.orm import declarative_base, declared_attr

class CustomBase:
    @declared_attr
    def __tablename__(cls) -> str:
        # Convert CamelCase to snake_case
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

Base = declarative_base(cls=CustomBase)
