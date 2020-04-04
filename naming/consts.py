# Global constants file
from typing import Dict, Any
import queue

boolReturn = {"success": None}
exceptionReturn = {"exception_type": None, "exception_info": None}

# #json helper
# registerRequest = {"storage_ip": None, "client_port": None, "command_port" : None, "files" : []}
# filesReturn = {"files" : []}

# List of dictionaries
storageServers = []


# Nested dictionary
filesDict: Dict[Any, Any] = {}

# queue of lock requests
q = queue.Queue()




