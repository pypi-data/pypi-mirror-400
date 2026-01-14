from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import yaml

class HeaderFooterOptions(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    header_left: Optional[str] = Field(default=None, description="Left header content")
    header_center: Optional[str] = Field(default=None, description="Center header content")
    header_right: Optional[str] = Field(default=r"Page \thepage \ of \ \pageref{LastPage}", description="Right header content")
    footer_left: Optional[str] = Field(default=None, description="Left footer content")
    footer_center: Optional[str] = Field(default=None, description="Center footer content")
    footer_right: Optional[str] = Field(default=None, description="Right footer content")