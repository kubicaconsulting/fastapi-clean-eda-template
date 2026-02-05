"""Domain events for event-driven architecture."""

from dataclasses import dataclass
from datetime import date, timedelta


class BusinessRuleValidationException(Exception):
    """A base class for all business rule validation exceptions"""


@dataclass(frozen=True)
class DateRange:
    """Our first value object"""

    start_date: date
    end_date: date

    def __post_init__(self):
        """Here we check if a value object has a valid state."""
        if not self.start_date < self.end_date:
            raise BusinessRuleValidationException(
                "end date date should be greater than start date"
            )

    def days(self):
        """Returns the number of days between the start date and the end date"""
        delta = self.end_date - self.start_date + timedelta(days=1)
        return delta.days

    def extend(self, days):
        """Extend the end date by a specified number of days"""
        new_end_date = self.end_date + timedelta(days=days)
        return DateRange(self.start_date, new_end_date)
