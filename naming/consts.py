# Global constants file
from typing import Dict, Any
import queue

boolReturn = {"success": None}
exceptionReturn = {"exception_type": None, "exception_info": None}


# List of storage servers
storageServers = []

# queue of lock requests
q = queue.Queue()
lockId = 0

# Maintains access count for shared locks
AccessCount = dict()
ReplicatedFiles = dict()



