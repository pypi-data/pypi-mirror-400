from typing import final

from tortoise import fields, models
from typing_extensions import override


class TimeStampedModel:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(blank=True, null=True)


class BaseModel(models.Model, TimeStampedModel):
    id = fields.BigIntField(index=True, primary_key=True)

    class Meta:
        abstract = True


@final
class ExtractedPage(BaseModel):
    url = fields.TextField(indexable=True)
    title = fields.TextField(null=True)
    channel = fields.CharField(max_length=255, null=True)

    @override
    def __str__(self) -> str:
        return self.title
