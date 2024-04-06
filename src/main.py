
from __future__ import annotations
from dataclasses import dataclass
import logging
from os.path import expanduser
from typing import Any, List

from kivy.utils import platform

from app import BankOpRegisterer

if platform == "android":
    import android
    from android.permissions import Permission, check_permission
    from android.storage import primary_external_storage_path

@dataclass
class PermDef():
    perm: Any
    name: str

if platform == "android":
    PERM_DEF_LIST = [
        PermDef(Permission.READ_EXTERNAL_STORAGE, "READ_EXTERNAL_STORAGE"),
        PermDef(Permission.WRITE_EXTERNAL_STORAGE, "WRITE_EXTERNAL_STORAGE"),
    ]

def main():

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("main")

    if platform == "android":
        for perm_def in PERM_DEF_LIST:
            if not check_permission(perm_def.perm):
                logger.error("main: check_permission %s FAILED", perm_def.name)
                exit()

    if platform == "android":
        base_dir_path = f"{primary_external_storage_path()}/Documents"
    else:
        base_dir_path = expanduser('~')
    logger.debug("main: base_dir_path = %s", base_dir_path)

    bank_op_register = BankOpRegisterer(base_dir_path)
    bank_op_register.run()

if __name__ == "__main__":
    main()
