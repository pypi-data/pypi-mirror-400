from mcqpy.question.filter.base_filter import AttributeFilter
from enum import Enum

class DifficultyLevel(Enum):
    """Difficulty levels with ordering."""
    VERY_EASY = 0
    EASY = 1
    MEDIUM = 2
    HARD = 3
    VERY_HARD = 4
    
    @classmethod
    def from_string(cls, value: str) -> 'DifficultyLevel':
        """Convert string to DifficultyLevel."""
        return cls[value.upper().replace(" ", "_")]


class DifficultyFilter(AttributeFilter):
    """Filter questions by difficulty level with comparison operators.
    
    Supports:
    - Exact match: DifficultyFilter('hard')
    - Less than: DifficultyFilter('<hard') or DifficultyFilter('hard', operator='<')
    - Less than or equal: DifficultyFilter('<=hard')
    - Greater than: DifficultyFilter('>easy')
    - Greater than or equal: DifficultyFilter('>=easy')
    
    Args:
        difficulty: Difficulty level to filter by
        operator: Comparison operator (==, <, <=, >, >=)
        strict_missing: If True (default), exclude questions without difficulty attribute.
                        If False, include questions without difficulty attribute.
    """
    
    OPERATORS = {
        '==': lambda a, b: a == b,
        '<': lambda a, b: a < b,
        '<=': lambda a, b: a <= b,
        '>': lambda a, b: a > b,
        '>=': lambda a, b: a >= b,
    }
    
    def __init__(self, difficulty: str, operator: str = '==', strict_missing: bool = True):
        # Parse operator from string if present
        if difficulty.startswith(('<=', '>=', '<', '>')):
            for op in ['<=', '>=', '<', '>']:
                if difficulty.startswith(op):
                    operator = op
                    difficulty = difficulty[len(op):].strip()
                    break
        
        self.difficulty = difficulty
        self.operator = operator
        self.target_level = DifficultyLevel.from_string(difficulty)
        self.strict_missing = strict_missing
        super().__init__('difficulty', difficulty, self._difficulty_predicate)
    
    def _difficulty_predicate(self, question_difficulty, _):
        if not question_difficulty:
            return not self.strict_missing
        q_level = DifficultyLevel.from_string(question_difficulty)
        comparison_func = self.OPERATORS[self.operator]
        
        return comparison_func(q_level.value, self.target_level.value)
