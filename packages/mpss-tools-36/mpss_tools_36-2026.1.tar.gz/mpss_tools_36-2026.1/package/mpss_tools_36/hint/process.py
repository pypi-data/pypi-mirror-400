"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from multiprocessing import Process as process_t
from multiprocessing import current_process as CurrentProcess

# Curiously, a multiprocessing.Process is of type multiprocessing.context.Process while
# the current process is of type multiprocessing.process._MainProcess, and
# isinstance(multiprocessing.current_process(), multiprocessing.Process) is False.
process_h = process_t | type[CurrentProcess()]
