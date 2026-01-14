from mcqpy.question.filter.base_filter import BaseFilter
from mcqpy.question import Question
from datetime import date

class DateFilter(BaseFilter):
    """Filter questions by creation date.
    
    Supports:
    - Exact year: DateFilter('2024') - matches all dates in that year
    - Exact date: DateFilter('15/03/2024')
    - Before date: DateFilter('<2024') or DateFilter('<15/03/2024')
    - After date: DateFilter('>2023') or DateFilter('>01/01/2023')
    - Date range: DateFilter('2023', '2024')
    
    Note: All dates are stored internally as 'dd/mm/yyyy' format.
    Year-only inputs are treated as the full year range (Jan 1 - Dec 31).
    """
    
    OPERATORS = {
        '==': lambda a, b: a == b,
        '<': lambda a, b: a < b,
        '<=': lambda a, b: a <= b,
        '>': lambda a, b: a > b,
        '>=': lambda a, b: a >= b,
    }
    
    def __init__(self, date_value: str, end_date: str = None, strict_missing: bool = True):
        """Initialize date filter.
        
        Args:
            date_value: Date string ('yyyy' or 'dd/mm/yyyy'), may include operator prefix
            end_date: Optional end date for range queries
            operator: Comparison operator (if not in date_value)
            strict_missing: If True (default), exclude questions without created_date attribute.
                           If False, include questions without created_date attribute.
        """
        # Parse operator from string if present
        parsed_operator, parsed_date = self._parse_date_operator(date_value)
        
        self.operator = parsed_operator
        self.strict_missing = strict_missing
        self.start_date = self._parse_date_range(parsed_date)
        self.end_date = self._parse_date_range(end_date) if end_date else None
        self.is_range = end_date is not None


    def _parse_date_operator(self, date_value: str) -> tuple[str, str]:
        if date_value.startswith(('<=', '>=', '<', '>')):
            for op in ['<=', '>=', '<', '>']:
                if date_value.startswith(op):
                    operator = op
                    date_value = date_value[len(op):].strip()
                    break
        else:
            operator = '=='
        return operator, date_value
    
    
    def _parse_date_range(self, date_str: str) -> tuple[date, date]:
        """Parse date string to tuple of (start_date, end_date) representing the range.
        
        For year-only ('2024'): returns (Jan 1, Dec 31) of that year
        For full date ('15/03/2024'): returns (date, date) - same date for both
        """
        # Check if year-only
        if len(date_str) == 4 and date_str.isdigit():
            year = int(date_str)
            return (date(year, 1, 1), date(year, 12, 31))
        
        # Parse dd/mm/yyyy
        parts = date_str.split('/')
        day, month, year = map(int, parts)
        d = date(year, month, day)
        return (d, d)
    
    def _parse_stored_date(self, date_str: str) -> date:
        """Parse stored date format (dd/mm/yyyy) to date object."""
        parts = date_str.split('/')
        day, month, year = map(int, parts)
        return date(year, month, day)
    
    def _matches_date(self, question_date_str: str) -> bool:
        """Check if question date matches filter criteria.
        
        Note: question_date_str is always in 'dd/mm/yyyy' format (normalized during validation).
        """
        q_date = self._parse_stored_date(question_date_str)
        
        if self.is_range:
            # Range query: question date must be within filter range
            filter_start = min(self.start_date[0], self.end_date[0])
            filter_end = max(self.start_date[1], self.end_date[1])
            return filter_start <= q_date <= filter_end
        
        # Single comparison
        comparison_func = self.OPERATORS[self.operator]
        target_start, target_end = self.start_date
        
        if self.operator == '==':
            # For equality, check if question date falls within target range
            return target_start <= q_date <= target_end
        elif self.operator in ['<', '<=']:
            # Compare against end of target range
            return comparison_func(q_date, target_end)
        else:  # '>', '>='
            # Compare against start of target range
            return comparison_func(q_date, target_start)
    
    def apply(self, questions: list[Question]) -> list[Question]:
        """Apply date filter to questions."""
        result = []
        for q in questions:
            if q.created_date:
                if self._matches_date(q.created_date):
                    result.append(q)
            elif not self.strict_missing:
                result.append(q)
        return result