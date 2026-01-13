from sqlalchemy import Boolean, Column, SmallInteger
from sqlalchemy.dialects.postgresql import JSON

from .base import Base, IdentityBase, Sources, TimeSign, Types


class RawMeasurement(IdentityBase, TimeSign, Base):
    __tablename__ = "measurement_raw"

    data = Column(JSON)
    type = Column(SmallInteger)
    source = Column(
        SmallInteger, nullable=False, server_default=str(Sources.sensorhub.value)
    )
    is_processed = Column(Boolean, default=False)

    @property
    def source_enum(self):
        return Sources(self.source)

    @source_enum.setter
    def source_enum(self, source_enum):
        self.source = source_enum.value

    @property
    def type_enum(self):
        return Types(self.type)

    @type_enum.setter
    def type_enum(self, type_enum):
        self.type = type_enum.value
