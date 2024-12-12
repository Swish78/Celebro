from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Annotated, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.str_schema(),
            core_schema.json_or_python_schema(
                json_schema=core_schema.str_schema(),
                python_schema=core_schema.union_schema([
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.str_schema(),
                ]),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    lambda x: str(x)
                )
            )
        ])

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler
    ):
        return {"type": "string"}

    def __str__(self):
        return str(self)


class QueryCreate(BaseModel):
    query: str
    web_results: List[Dict]
    ai_answer: str


class QueryResponse(QueryCreate):
    id: Annotated[PyObjectId, Field(alias="_id")]
    user_id: str
    created_at: datetime

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class QueryFilter(BaseModel):
    days: int = 30
    page: int = 1
    page_size: int = 10