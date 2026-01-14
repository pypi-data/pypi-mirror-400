from mcqpy.question.filter.base_filter import AttributeFilter

class SlugFilter(AttributeFilter):
    """Filter questions by slug with exact match.
    
    Args:
        slug: Slugs to filter by
    """
    
    def __init__(self, slugs: list[str]):
        self.slugs = slugs
        super().__init__('slug', slugs, self._slug_predicate)
    
    def _slug_predicate(self, question_slug, _):
        return question_slug in self.slugs