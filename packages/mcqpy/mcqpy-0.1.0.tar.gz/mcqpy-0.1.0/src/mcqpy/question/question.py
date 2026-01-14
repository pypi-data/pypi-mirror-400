from pathlib import Path
from typing import Any, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator, model_serializer
import uuid
from datetime import date as dt_date

from mcqpy.question import (
    Image,
    ImageOptions,
    ImageCaptions,
    _norm_images,
    _norm_opts,
    _norm_caps,
    relativize_paths
)

# Commit one namespace UUID for your course/repo (don’t change later)
COURSE_NAMESPACE = uuid.UUID("9f1e0d8c-7f3a-4c02-be3b-3f8f5a2a8f2e")

ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".tif", ".tiff"}


def qid_from_slug(slug: str) -> str:
    return str(uuid.uuid5(COURSE_NAMESPACE, slug))


class Question(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid"
    )  # make instances immutable (optional but helpful)

    # Identity
    slug: str = Field(..., description="Immutable short key chosen at creation")
    qid: str = Field(..., description="Stable UUIDv5 derived from slug")

    # Content
    text: str = Field(..., description="Question text, may contain LaTeX")
    choices: List[str] = Field(..., min_length=2, description="Answer choices")
    correct_answers: List[int] = Field(
        ...,
        min_length=1,
        description="Indices of correct answers in `choices`, 0-based",
    )
    question_type: Literal["single", "multiple"] = Field(
        ...,
        description="Type of question: 'single' for single-choice, 'multiple' for multiple-choice",
    )

    # Images
    image: Image = Field(
        None, description="Path(s) to image file(s) associated with the question"
    )
    image_options: ImageOptions = Field(
        None, description="Options for image(s) display, e.g., width, height"
    )
    image_caption: ImageCaptions = Field(
        None, description="Caption(s) for each image(s), if any"
    )

    # Code: 
    code: list[Optional[str]] | Optional[str] = Field(
        None, description="Code snippet associated with the question"
    )
    code_language: Optional[list[str]] | Optional[str] = Field(
        None, description="Programming language of the code snippet(s)"
    )

    # Presentation
    permutation: List[int] | None = Field(
        None,
        description="If provided, specifies a permutation of the choices to present",
    )
    fixed_permutation: bool = Field(
        False, description="If true, do not permute the choices when presenting"
    )

    # Grading: 
    point_value: int = Field(1, ge=0, description="Point value of the question")

    # Metadata
    difficulty: Optional[Literal["very easy" ,"easy", "medium", "hard", "very hard"]] = None
    tags: Optional[List[str]] = None
    explanation: Optional[str] = None
    created_date: Optional[str] = Field(
        None, 
        description="Date question was created. Stored as 'dd/mm/yyyy' (input accepts 'yyyy' or 'dd/mm/yyyy')"
    )
    comment: Optional[str] = Field(
        None, description="Internal comment for instructors/editors"
    )
    path: Optional[str | Path] = Field(
        None, description="Internal: file path from which this question was loaded", exclude=True)

    @model_validator(mode="before")
    @classmethod
    def _normalize_media_fields(cls, data: Any):
        # Pull raw inputs (may be absent/None/union-shaped)
        raw_img = data.get("image")
        raw_opts = data.get("image_options")
        raw_caps = data.get("image_caption")

        # Normalize
        norm_img = _norm_images(raw_img)
        norm_opts = _norm_opts(raw_opts)
        norm_caps = _norm_caps(raw_caps)

        # Optional sanity check: indices referenced by opts/caps must exist in images
        if norm_img:
            max_idx = len(norm_img) - 1
            for src_name, idxs in (
                ("image_options", norm_opts.keys()),
                ("image_captions", norm_caps.keys()),
            ):
                if norm_img and -1 in idxs:
                    continue  # -1 is always valid if we have images (for global caption)
                bad = [i for i in idxs if i < 0 or i > max_idx]
                if bad:
                    raise ValueError(
                        f"{src_name} contains out-of-range indices {bad}; "
                        f"valid range is 0..{max_idx} (got {len(norm_img)} images)."
                    )

        # Write back normalized values so field parsing sees canonical shapes
        data["image"] = norm_img
        data["image_options"] = norm_opts
        data["image_caption"] = norm_caps
        return data

    @model_validator(mode="before")
    @classmethod
    def _derive_qid(cls, data: dict):
        """
        - If qid missing: compute it from slug.
        - If qid provided: verify it matches the computed one.
        """
        if "slug" not in data:
            raise ValueError("slug is required to derive qid")

        expected = qid_from_slug(data["slug"])
        provided = data.get("qid")

        if provided is None:
            data["qid"] = expected
        elif provided != expected:
            raise ValueError(
                f"Provided qid does not match slug-derived qid.\n"
                f"  slug: {data['slug']}\n"
                f"  expected: {expected}\n"
                f"  provided: {provided}"
            )
        return data

    @model_validator(mode="before")
    @classmethod
    def _validate_derive_permutation(cls, data: dict):
        """
        If permutation is not provided, set it to the identity permutation.
        """
        if data.get("permutation") is None:
            data["permutation"] = list(range(len(data["choices"])))
        return data

    @field_validator("image")
    @classmethod
    def validate_image(cls, v: Optional[str], info):
        if not v:
            return v

        if not isinstance(v, list):
            v = [v]

        full_paths = []
        for item in v:

            # Check if a web URL
            if isinstance(item, str) and (item.startswith("http://") or item.startswith("https://")):
                full_paths.append(item)
                continue

            p = Path(item)
            # Resolve relative to the YAML file directory, if provided via context
            base_dir = info.context.get("base_dir", Path.cwd())
            resolved = p if p.is_absolute() else (base_dir / p).resolve()

            if not resolved.exists() or not resolved.is_file():
                raise FileNotFoundError(f"Image not found: {v} (resolved to: {resolved})")
            if resolved.suffix.lower() not in ALLOWED_IMAGE_EXTS:
                raise ValueError(
                    f"Unsupported image extension '{resolved.suffix}'. "
                    f"Allowed: {sorted(ALLOWED_IMAGE_EXTS)}"
                )
            full_paths.append(str(resolved))

        return full_paths
    
    @model_serializer(mode="wrap")
    def serialize_model(self, serializer, info):
        """Custom serializer to convert absolute image paths to relative paths."""
        data = serializer(self)
        
        # Only convert paths if we have a base path (i.e., loaded from YAML)
        if self.path and self.image:
            base_dir = Path(self.path).resolve().parent
            data["image"] = relativize_paths(base_dir, self.image)
        
        return data

    @classmethod
    def load_yaml(cls, filepath: str) -> "Question":
        """Load a Question from a YAML file."""
        import yaml

        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        data['path'] = Path(filepath)  # Store the source file path

        return cls.model_validate(data, context={"base_dir": Path(filepath).parent})

    def as_yaml(self, path=None) -> str:
        """Serialize the Question to a YAML string."""
        import yaml
        data = self.model_dump()
        if path is not None:
            # Convert absolute image paths to relative paths based on provided path
            if self.image:
                base_dir = Path(path).resolve().parent
                rel_images = relativize_paths(base_dir, self.image)
                data = self.model_dump()
                data["image"] = rel_images

        return yaml.safe_dump(data, sort_keys=False)
    
    def save(self, path: str):
        """Save the Question to a YAML file."""
        yaml_str = self.as_yaml(path=path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(yaml_str)

    @classmethod
    def get_yaml_template(cls) -> str:
        """Get the YAML schema for the Question model, generated from the model's schema."""
        import yaml
        
        lines = ["# Question Template (auto-generated from model schema)", ""]
        
        schema = cls.model_json_schema()
        properties = schema.get("properties", {})
        required_fields = set(schema.get("required", []))
        
        # Helper to get example value based on type
        def get_example_value(field_name: str, field_info: dict):
            field_type = field_info.get("type")
            
            # Special cases based on field name
            if field_name == "slug":
                return "my-unique-question-slug"
            elif field_name == "text":
                return "Your question text here (LaTeX supported)"
            elif field_name == "choices":
                return ["Answer choice 1", "Answer choice 2", "Answer choice 3", "Answer choice 4"]
            elif field_name == "correct_answers":
                return [0]
            elif field_name == "question_type":
                enum_vals = field_info.get("enum", [])
                return enum_vals[0] if enum_vals else "single"
            elif field_name == "image":
                return "path/to/image.png"
            elif field_name == "image_options":
                return {0: {"width": "0.5\\textwidth"}}
            elif field_name == "image_caption":
                return {-1: "Caption for all images"}
            elif field_name == "code":
                return "print('Hello, world!')"
            elif field_name == "code_language":
                return "python"
            elif field_name == "permutation":
                return None  # Auto-generated
            elif field_name == "fixed_permutation":
                return False
            elif field_name == "point_value":
                return field_info.get("default", 1)
            elif field_name == "difficulty":
                return "medium"
            elif field_name == "tags":
                return ["tag1", "tag2"]
            elif field_name == "explanation":
                return "Optional explanation of the correct answer"
            
            return None
        
        # Process fields in order
        for field_name, field_info in properties.items():
            if field_name == "qid":
                continue  # Skip qid as it's auto-generated
            
            is_required = field_name in required_fields
            description = field_info.get("description", "")
            example_value = get_example_value(field_name, field_info)
            
            # Add section header comments
            if is_required:
                lines.append(f"# {field_name} (Required)")
            else:
                lines.append(f"# {field_name} (Optional)")
            
            if description:
                lines.append(f"# {description}")
            
            # Add the field
            if example_value is not None:
                if is_required:
                    yaml_str = yaml.dump({field_name: example_value}, sort_keys=False, default_flow_style=False).strip()
                    lines.append(yaml_str)
                else:
                    yaml_str = yaml.dump({field_name: example_value}, sort_keys=False, default_flow_style=False).strip()
                    # Comment out optional fields
                    for line in yaml_str.split('\n'):
                        lines.append(f"# {line}")
            
            lines.append("")  # Blank line between fields
        
        return "\n".join(lines)

    @model_validator(mode="before")
    @classmethod
    def validate_code(cls, data: dict):
        """
        Ensure that if code is provided as a single string, it is converted to a list.
        Similarly for code_language.
        """
        # Normalize code
        raw_code = data.get("code")
        if raw_code is not None and not isinstance(raw_code, list):
            data["code"] = [raw_code]

        # Normalize code_language
        raw_lang = data.get("code_language")
        if raw_lang is not None and not isinstance(raw_lang, list):
            data["code_language"] = [raw_lang]

        return data
    
    @field_validator("created_date")
    @classmethod
    def validate_and_normalize_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize date to 'dd/mm/yyyy' format.
        
        Accepts:
        - 'yyyy' -> normalized to '01/01/yyyy'
        - 'dd/mm/yyyy' -> validated and returned as-is
        """
        if v is None:
            return v
        
        # Try year-only format first
        if len(v) == 4 and v.isdigit():
            year = int(v)
            if not (1900 <= year <= 2100):
                raise ValueError(f"Year {year} is outside reasonable range (1900-2100)")
            # Normalize to dd/mm/yyyy format (use January 1st)
            return f"01/01/{year}"
        
        # Try dd/mm/yyyy format
        try:
            parts = v.split('/')
            if len(parts) != 3:
                raise ValueError("Date must be in format 'dd/mm/yyyy' or 'yyyy'")
            
            day, month, year = map(int, parts)
            # Validate using Python's date
            dt_date(year, month, day)
            return v
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Invalid date format: '{v}'. Use 'dd/mm/yyyy' or 'yyyy'"
            ) from e

