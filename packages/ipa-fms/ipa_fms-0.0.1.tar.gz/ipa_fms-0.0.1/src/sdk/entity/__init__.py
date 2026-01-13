import time
from typing import List, Optional

from sqlmodel import Field, SQLModel


def timestamp_ms(value_type=float):
    return value_type(time.time() * 1000)


class FileEntity(SQLModel, table=True):
    __tablename__ = "file"

    id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )

    file_no: str = Field(
        description="文件编号", nullable=False, unique=True, max_length=64
    )
    type: Optional[str] = Field(None, description="文件类型", max_length=64)
    name: str = Field(description="文件名", max_length=128)
    url: Optional[str] = Field(None, description="地址", max_length=256)

    created_at: float = Field(
        description="创建时间",
        nullable=False,
        default_factory=lambda: timestamp_ms(int),
    )
    updated_at: float = Field(
        description="更新时间",
        nullable=False,
        default_factory=lambda: timestamp_ms(int),
        sa_column_kwargs={"onupdate": timestamp_ms(int)},
    )
    deleted_at: Optional[float] = Field(default=None, description="删除时间")

    user_id: Optional[str] = Field(default=None, max_length=64)

    tags: Optional[str] = Field(default=None, description="标签", max_length=128)
    remark: Optional[str] = Field(default=None, description="备注", max_length=256)
