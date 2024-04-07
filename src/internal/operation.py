
from datetime import datetime

class Operation:
    """Operation"""

    CSV_KEY_DATE = "date"
    CSV_KEY_MODE = "mode"
    CSV_KEY_TIER = "tier"
    CSV_KEY_CAT = "category"
    CSV_KEY_DESC = "description"
    CSV_KEY_AMOUNT = "amount"

    CSV_KEY_LIST = [
        CSV_KEY_DATE,
        CSV_KEY_MODE,
        CSV_KEY_TIER,
        CSV_KEY_CAT,
        CSV_KEY_DESC,
        CSV_KEY_AMOUNT,
    ]

    TIME_FMT = "%Y-%m-%d"

    def __init__(self, date: datetime = datetime.now(), mode: str = "", tier: str = "",
        category: str = "", description: str = "", amount: float = 0.0):

        self.date = date
        self.mode = mode
        self.tier = tier
        self.category = category
        self.description = description
        self.amount = amount

    @classmethod
    def from_csv(cls, csv_entry: dict):
        """Create Operation from CSV entry"""
        return Operation(
            datetime.strptime(csv_entry[cls.CSV_KEY_DATE], cls.TIME_FMT),
            csv_entry[cls.CSV_KEY_MODE],
            csv_entry[cls.CSV_KEY_TIER],
            csv_entry[cls.CSV_KEY_CAT],
            csv_entry[cls.CSV_KEY_DESC],
            float(csv_entry[cls.CSV_KEY_AMOUNT]),
        )

    def as_csv(self) -> dict:
        """Get as CSV entry"""
        return {
            self.CSV_KEY_DATE: self.date.strftime(self.TIME_FMT),
            self.CSV_KEY_MODE: self.mode,
            self.CSV_KEY_TIER: self.tier,
            self.CSV_KEY_CAT: self.category,
            self.CSV_KEY_DESC: self.description,
            self.CSV_KEY_AMOUNT: str(self.amount),
        }

    def __str__(self) -> str:
        return (f"{self.date.strftime(self.TIME_FMT)}, {self.mode}, {self.tier}, "
            f"{self.category}, {self.description}, {self.amount}")
