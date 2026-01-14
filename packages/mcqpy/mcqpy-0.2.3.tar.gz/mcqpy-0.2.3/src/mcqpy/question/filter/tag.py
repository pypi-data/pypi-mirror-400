from mcqpy.question.filter.base_filter import AttributeFilter


class TagFilter(AttributeFilter):
    """Filter questions by tag(s).

    Supports:
    - Include any: TagFilter(['python', 'loops'])
    - Include all: TagFilter(['python', 'loops'], match_all=True)
    - Exclude any: TagFilter(['deprecated'], exclude=True)

    Args:
        tags: Tag(s) to filter by
        match_all: If True, question must have all specified tags
        exclude: If True, exclude questions with any of the specified tags
        strict_missing: If True (default), exclude questions without tags attribute (unless exclude=True).
                        If False, include questions without tags attribute (unless exclude=True).
    """

    def __init__(
        self,
        tags: list[str] | str,
        match_all: bool = False,
        exclude: bool = False,
        strict_missing: bool = True,
    ):
        self.tags = [tags] if isinstance(tags, str) else tags
        self.match_all = match_all
        self.exclude = exclude
        self.strict_missing = strict_missing

        super().__init__("tags", self.tags, self._tag_predicate)

    def _tag_predicate(self, question_tags, filter_tags):
        if not question_tags:
            # When excluding: no tags means it passes (no excluded tags present)
            # When including: use strict_missing parameter
            if self.exclude:
                return True
            return not self.strict_missing

        if self.exclude:
            # Exclude if ANY of the filter tags are present
            has_excluded = any(tag in question_tags for tag in filter_tags)
            return not has_excluded

        if self.match_all:
            return all(tag in question_tags for tag in filter_tags)
        return any(tag in question_tags for tag in filter_tags)
