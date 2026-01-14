import json
import sys
from pathlib import Path

import tornado
from jupyter_server.base.handlers import APIHandler


class QiskitConfigHandler(APIHandler):
    """Handler for reading Qiskit IBM configuration."""
    
    @tornado.web.authenticated
    def get(self):
        """Get Qiskit IBM configuration."""
        config = self.get_qiskit_config()
        self.finish(json.dumps(config))
    
    @staticmethod
    def get_qiskit_config():
        """
        Retrieve the user's Qiskit IBM configuration.
        
        Returns:
            A dictionary containing Qiskit IBM configuration.
        """
        try:
            qiskit_config_path = Path.home().joinpath(".qiskit", "qiskit-ibm.json")
            if qiskit_config_path.exists():
                with open(qiskit_config_path, 'r') as f:
                    config = json.load(f)
                return config
            else:
                return {"error": "Qiskit IBM configuration file not found."}
        except Exception as e:
            print(f"Error while retrieving Qiskit IBM configuration: {str(e)}", file=sys.stderr)
            return {"error": str(e)}