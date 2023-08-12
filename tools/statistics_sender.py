# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

from typing import Any

import requests

from .settings import Settings


class StatisticsSender:
    """
    Sender for statistics
    """

    TARGET_URL: str = "http://statistics.molodos.com:8090/cura"

    @classmethod
    def send_statistics(cls, settings: Settings) -> None:
        """
        Sends anonymous statistics
        """
        # Collect statistics
        statistics: dict[str, Any] = {
            "plugin": settings.plugin_json["id"],
            "version": settings.plugin_json["version"],
            "id": settings.statistics_id,
            "printer": settings.get_printer_model_id(),
            "options": settings.get_corner_option_ids()
        }

        # Send statistics
        try:
            requests.post(url=cls.TARGET_URL, json=statistics, timeout=1)
        except Exception:
            pass
