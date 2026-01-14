from pydantic import BaseModel, Field, ConfigDict
import yaml
from mcqpy.compile import HeaderFooterOptions, FrontMatterOptions
from typing import Any, Literal

class SelectionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    number_of_questions: int | None = Field(default=20, description="Number of questions to select")
    filters: dict[str, dict[str, Any]] | None = Field(default=None, description="Filters to apply when selecting questions")
    seed: int | None = Field(default=None, description="Random seed for question selection")
    shuffle: bool = Field(default=False, description="Whether to shuffle selected questions")
    sort_type: Literal['slug', 'none'] = Field(default='none', description="Sort type for selected questions")

class QuizConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    questions_paths: list[str] | str = Field(default=["questions"], description="Paths to question files or directories")
    file_name: str = Field(default="quiz.pdf", description="Name of the output PDF file")
    root_directory: str = Field(default=".", description="Root directory for the quiz project")
    output_directory: str = Field(default="output", description="Directory for output files")
    submission_directory: str | None = Field(default=None, description="Directory for submission files (if any)")
    front_matter: FrontMatterOptions = Field(default_factory=FrontMatterOptions)
    header: HeaderFooterOptions = Field(default_factory=HeaderFooterOptions)
    selection: SelectionConfig = Field(default_factory=SelectionConfig)

    def yaml_dump(self) -> str:
        """Dump the current configuration to a YAML string"""
        config_dict = self.model_dump()
        yaml_content = yaml.dump(config_dict, default_flow_style=False, sort_keys=False)
        return yaml_content

    @classmethod
    def generate_example_yaml(cls) -> str:
        """Generate example YAML with comments"""
        example = cls()
        return example.yaml_dump()

    @classmethod
    def read_yaml(cls, file_path: str) -> "QuizConfig":
        """Read YAML file and return a QuizConfig instance"""
        with open(file_path, "r") as file:
            yaml_string = file.read()
        data = yaml.safe_load(yaml_string)
        return cls(**data)