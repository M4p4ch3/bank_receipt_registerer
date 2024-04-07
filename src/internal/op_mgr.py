
import csv
import logging
from typing import List

from .operation import Operation

class OpMgr():
    """Operations list manager"""

    def __init__(self, file_path: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.file_path = file_path
        self.logger.debug("OpMgr: file_path = %s", self.file_path)
        self.op_list: List[Operation] = []
        self.load()

    def add_operation(self, operation: Operation):
        """Add operation"""
        self.logger.debug("OpMgr: add Operation(%s)", operation)
        self.op_list += [operation]

    def delete_operation(self, operation: Operation):
        """Delete operation"""
        self.logger.debug("OpMgr: delete Operation(%s)", operation)
        self.op_list.remove(operation)

    def load(self):
        """Load operations list from file"""

        self.logger.debug("OpMgr: load")
        self.op_list.clear()

        # Ensure file exists by opening in write mode
        # Write append mode to avoid overriding
        with open(self.file_path, mode="a", encoding="utf8"):
            pass

        with open(self.file_path, mode="r", encoding="utf8") as op_list_file:
            op_list_csv_reader = csv.DictReader(op_list_file)
            for op_csv_entry in op_list_csv_reader:
                self.op_list += [Operation.from_csv(op_csv_entry)]

    def save(self):
        """Save operations list to file"""
        self.logger.debug("OpMgr: save")
        with open(self.file_path, mode="w", encoding="utf8") as op_list_file:
            op_list_csv_writer = csv.DictWriter(op_list_file, fieldnames=Operation.CSV_KEY_LIST)
            op_list_csv_writer.writeheader()
            for operation in self.op_list:
                op_list_csv_writer.writerow(operation.as_csv())
