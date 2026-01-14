import os
import time
from pathlib import Path
from dxtr.utils.logging import logger

# here = Path(os.path.dirname(__file__))
# root = list(here.parents)[1]
# log_path = root.joinpath('log/')

# if not log_path.is_dir():
#     log_path.mkdir() 

# time_stamp = time.strftime("%y%m%d")
# file_name = '.'.join((time_stamp, 'log'))
# log_file = log_path.joinpath(file_name)

# logger = get_logger(__name__, log_file=log_file)

from .complexes import (Simplex, AbstractSimplicialComplex, SimplicialComplex, 
                      SimplicialManifold)
from .cochains import Cochain
