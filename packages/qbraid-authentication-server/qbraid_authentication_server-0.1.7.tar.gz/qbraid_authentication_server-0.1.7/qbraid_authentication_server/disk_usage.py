# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Script to anaylze disk usage and report to computer manger.

"""

import asyncio
import json
import logging
from pathlib import Path

import tornado
from jupyter_server.base.handlers import APIHandler
from qbraid_core import QbraidException
from qbraid_core.services.storage import DiskUsageClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


async def report_disk_usage():
    """Run the disk usage report using DiskUsageClient."""
    try:
        home = Path.home()

        client = DiskUsageClient()

        # Get disk usage for home directory
        total_gb = await client.get_disk_usage_gb(home)

        # Report disk usage to API
        resp_data = await client.report_disk_usage(total_gb)

        logger.info("Disk usage report response: %s", resp_data)
    except (Exception, QbraidException) as e:
        raise RuntimeError(f"Error reporting disk usage: {e}") from e


class DiskUsageHandler(APIHandler):
    """Handler for reporting disk usage to the qBraid API."""

    @tornado.web.authenticated
    async def put(self):
        """Get disk usage for a users home directory."""

        response_data = {"status": 202, "message": "Disk usage reporting initiated successfully"}

        try:
            asyncio.create_task(report_disk_usage())
        except RuntimeError as e:
            logger.error("Error reporting disk usage: %s", e)
            response_data = {"status": 500, "error": str(e)}
        except ValueError as e:
            logger.error("Invalid input: %s", e)
            response_data = {"status": 500, "error": str(e)}
        except Exception as e:
            logger.error("Error getting disk usage: %s", e)
            response_data = {"status": 500, "error": str(e)}

        self.finish(json.dumps(response_data))
