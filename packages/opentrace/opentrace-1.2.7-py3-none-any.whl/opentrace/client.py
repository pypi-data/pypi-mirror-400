import requests
import json
import threading
import logging
import hashlib
from typing import Dict, Any, Optional, Union

logger = logging.getLogger("opentrace")

class OpenTrace:
    def __init__(self, host: str, project_id: Optional[str] = None, debug: bool = False):
        """
        Initialize OpenTrace Client.
        
        :param host: URL of your OpenTrace instance (e.g. https://analytics.yourdomain.com)
        :param project_id: Default Resource UID (optional)
        :param debug: Enable debug logging
        """
        self.host = host.rstrip('/')
        self.collect_endpoint = f"{self.host}/api/v1/collect"
        self.event_endpoint = f"{self.host}/api/v1/event"
        self.resolve_endpoint = f"{self.host}/api/campaigns/resolve"
        self.project_id = project_id
        self._session = requests.Session()
        
        if debug:
            logger.setLevel(logging.DEBUG)
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                logger.addHandler(handler)

    def get_user_hash(self, user_id: Union[str, int]) -> str:
        """
        Generate a persistent, anonymous hash for a user ID.
        Useful for privacy-first tracking of Telegram users.
        """
        return hashlib.sha256(str(user_id).encode()).hexdigest()[:16]

    def resolve_bot_param(self, param: str) -> Optional[Dict[str, str]]:
        """
        Resolve a Telegram bot 'start' parameter to UTM metadata.
        """
        try:
            # Clean utm_ prefix if present
            clean_param = param.replace("utm_", "") if param.startswith("utm_") else param
            response = self._session.get(f"{self.resolve_endpoint}/{clean_param}", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"OpenTrace Resolve Error: {e}")
            return None

    def track_event(self, 
                    name: str, 
                    project_id: str = None, 
                    payload: Dict[str, Any] = None,
                    utm_source: str = None,
                    utm_medium: str = None,
                    utm_campaign: str = None,
                    session_id: str = None,
                    bot_param: str = None):
        """
        Send a custom server-side event with full marketing attribution.
        """
        pid = project_id or self.project_id
        if not pid:
            logger.error("OpenTrace: No project_id/resource_id provided")
            return

        # If bot_param is provided and UTMs are missing, try to resolve them
        if bot_param and not utm_source:
             resolved = self.resolve_bot_param(bot_param)
             if resolved:
                 utm_source = resolved.get('utm_source')
                 utm_medium = resolved.get('utm_medium')
                 utm_campaign = resolved.get('utm_campaign')
                 if not payload: payload = {}
                 payload['bot_param'] = bot_param

        data = {
            "name": name,
            "project_id": str(pid),
            "payload": payload or {},
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_campaign": utm_campaign,
            "session_id": session_id
        }

        threading.Thread(target=self._send_request, args=(self.event_endpoint, data), daemon=True).start()

    def capture(self, 
                name: str, 
                payload: Dict[str, Any] = None, 
                resource_id: str = None, 
                user_id: str = None,
                fbclid: str = None,
                ttclid: str = None):
        """
        Send a telemetry event (web-style tracking for SDK parity).
        """
        rid = resource_id or self.project_id
        if not rid:
            logger.error("OpenTrace: No resource_id provided")
            return

        data = {
            "type": name,
            "rid": str(rid),
            "meta": payload or {},
            "fbclid": fbclid,
            "ttclid": ttclid
        }

        if user_id:
            data["sid"] = str(user_id)

        threading.Thread(target=self._send_request, args=(self.collect_endpoint, data), daemon=True).start()

    def _send_request(self, url, data):
        try:
            response = self._session.post(url, json=data, timeout=5)
            if response.status_code != 200:
                logger.warning(f"OpenTrace Failed: {response.status_code} {response.text}")
            else:
                event_name = data.get('name') or data.get('type')
                logger.debug(f"OpenTrace: Event '{event_name}' captured")
        except Exception as e:
            logger.error(f"OpenTrace Error: {e}")

    def track(self, name: str, payload: Dict[str, Any] = None, **kwargs):
        """ Alias for capture() """
        return self.capture(name, payload, **kwargs)
