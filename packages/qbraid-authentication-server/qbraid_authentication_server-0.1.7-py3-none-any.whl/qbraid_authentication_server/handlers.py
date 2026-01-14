from jupyter_server.utils import url_path_join

from .config import UserConfigHandler
from .disk_usage import DiskUsageHandler
from .qiskit_config import QiskitConfigHandler


def setup_handlers(web_app, url_path):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    qbraid_route_pattern = url_path_join(base_url, url_path, "qbraid-config")
    qbraid_disk_route_pattern = url_path_join(base_url, url_path, "qbraid-disk-usage")
    qiskit_config_route_pattern = url_path_join(base_url, url_path, "qiskit-config")
    handlers = [
        (qbraid_route_pattern, UserConfigHandler),
        (qbraid_disk_route_pattern, DiskUsageHandler),
        (qiskit_config_route_pattern, QiskitConfigHandler),
    ]
    web_app.add_handlers(host_pattern, handlers)
