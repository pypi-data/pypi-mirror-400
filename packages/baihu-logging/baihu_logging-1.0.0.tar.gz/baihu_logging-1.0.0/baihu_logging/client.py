import requests
from datetime import datetime
from .constants import LOG_COLORS, BASE_URL

class DiscordLogger:
    def __init__(self, token: str, channel_id: str):
        self.token = token
        self.channel_id = channel_id

        self._validate_config()

    def _validate_config(self):
        if not self.token:
            raise "Discord Token cannot be empty."

        if not self.channel_id:
            raise "Channel ID cannot be empty."

    def _send(self, level: str, title: str, message: str):
        if level not in LOG_COLORS:
            raise f"Invalid level: {level}. Available levels: {list(LOG_COLORS.keys())}"

        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "embeds": [
                {
                    "title": f"{title}",
                    "description": message,
                    "color": LOG_COLORS[level],
                    "timestamp": datetime.now().isoformat(),
                    "footer": {
                        "text": "Discord Logging Bot"
                    }
                }
            ]
        }

        url = f"{BASE_URL}/channels/{self.channel_id}/messages"
        response = requests.post(url, headers=headers, json=payload)
        
        if not response.ok:
            raise f"Discord API Error: {response.status_code}"
        
        return response

    def debug(self, title: str, message: str):
        return self._send("DEBUG", title, message)

    def info(self, title: str, message: str):
        return self._send("INFO", title, message)

    def warning(self, title: str, message: str):
        return self._send("WARNING", title, message)

    def error(self, title: str, message: str):
        return self._send("ERROR", title, message)

    def critical(self, title: str, message: str):
        return self._send("CRITICAL", title, message)