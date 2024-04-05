from typing_extensions import Annotated

from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, registry


bigint = Annotated[int, 64]

class Base(DeclarativeBase):

    registry = registry(
        type_annotation_map={
            bigint: BigInteger,
        },
    )
