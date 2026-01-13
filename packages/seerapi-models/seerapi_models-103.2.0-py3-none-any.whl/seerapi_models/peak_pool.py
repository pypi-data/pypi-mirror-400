from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from seerapi_models.build_model import BaseResModel, ConvertToORM
from seerapi_models.common import ResourceRef

if TYPE_CHECKING:
    from seerapi_models.pet import Pet, PetORM


class BasePeakPool(BaseResModel):
    count: int = Field(description='该池内精灵最大可携带数量')
    start_time: datetime = Field(description='该池的开始时间')
    end_time: datetime = Field(
        description='该池的结束时间，由 `start_time` 加上固定时长计算得出'
    )

    @classmethod
    def resource_name(cls) -> str:
        return 'peak_pool'


class PeakPool(BasePeakPool, ConvertToORM['PeakPoolORM']):
    pet: list[ResourceRef['Pet']] = Field(
        default_factory=list, description='该池内的精灵'
    )

    @classmethod
    def get_orm_model(cls) -> 'type[PeakPoolORM]':
        return PeakPoolORM

    def to_orm(self) -> 'PeakPoolORM':
        return PeakPoolORM(
            id=self.id,
            count=self.count,
            start_time=self.start_time,
            end_time=self.end_time,
        )


class PeakPoolORM(BasePeakPool, table=True):
    pet: list['PetORM'] = Relationship(back_populates='peak_pool')


class BasePeakExpertPool(BaseResModel):
    count: int = Field(description='该池内精灵最大可携带数量')
    start_time: datetime = Field(description='该池的开始时间')
    end_time: datetime = Field(
        description='该池的结束时间，由 `start_time` 加上固定时长计算得出'
    )

    @classmethod
    def resource_name(cls) -> str:
        return 'peak_expert_pool'


class PeakExpertPool(BasePeakExpertPool, ConvertToORM['PeakExpertPoolORM']):
    pet: list[ResourceRef['Pet']] = Field(
        default_factory=list, description='该池内的精灵'
    )

    @classmethod
    def get_orm_model(cls) -> 'type[PeakExpertPoolORM]':
        return PeakExpertPoolORM

    def to_orm(self) -> 'PeakExpertPoolORM':
        return PeakExpertPoolORM(
            id=self.id,
            count=self.count,
            start_time=self.start_time,
            end_time=self.end_time,
        )


class PeakExpertPoolORM(BasePeakExpertPool, table=True):
    pet: list['PetORM'] = Relationship(back_populates='peak_expert_pool')
