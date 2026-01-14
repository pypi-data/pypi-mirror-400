from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class FrontMatterOptions(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    title: Optional[str] = Field(default=None, description="Title of the document")
    author: Optional[str] = Field(default=None, description="Author of the document")
    date: Optional[str | bool] = Field(default=None, description="Date of the document")
    exam_information: Optional[str] = Field(default=None, description="Exam information")
    id_fields: bool = Field(default=False, description="Include ID fields")

