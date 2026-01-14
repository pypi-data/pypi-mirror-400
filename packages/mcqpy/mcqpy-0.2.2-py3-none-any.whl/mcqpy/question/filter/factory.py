from mcqpy.question.filter.base_filter import BaseFilter, CompositeFilter
from mcqpy.question.filter.difficulty import DifficultyFilter
from mcqpy.question.filter.tag import TagFilter
from mcqpy.question.filter.date import DateFilter
from mcqpy.question.filter.stratified import StratifiedFilter
from mcqpy.question.filter.manifest import ManifestFilter

class FilterFactory:
    """Creates filters from configuration dictionaries."""
    
    FILTER_MAP = {
        'difficulty': DifficultyFilter,
        'tag': TagFilter,
        'date': DateFilter,
        'stratified': StratifiedFilter,
        'manifest': ManifestFilter,
    }
    
    @classmethod
    def from_config(cls, config: dict) -> BaseFilter:
        """Create filter from config dict.
        """
        filter_type = config.get('type')
        
        if filter_type == 'composite':
            filters = [cls.from_config(f) for f in config['filters']]
            return CompositeFilter(filters)
        
        filter_class = cls.FILTER_MAP.get(filter_type)
        if not filter_class:
            raise ValueError(f"Unknown filter type: {filter_type}")
            
        kwargs = {k: v for k, v in config.items() if k not in ['type']}        
        return filter_class(**kwargs)