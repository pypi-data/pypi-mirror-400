import threading
import requests
import os
import json
import logging

logger = logging.getLogger("helm-analytics")

class HelmAnalytics:
    def __init__(self, site_id=None, api_url="https://api-sentinel.getmusterup.com"):
        self.site_id = site_id or os.getenv('HELM_SITE_ID')
        # Remove trailing slash and /track if present to get base URL
        self.api_url = api_url.rstrip('/').replace('/track', '')
        
        if not self.site_id:
            logger.warning("HelmAnalytics: No Site ID provided. Tracking will be disabled.")

    def _send_payload(self, payload, path="/track"):
        if not self.site_id:
            return
            
        def _post():
            try:
                requests.post(
                    f"{self.api_url}{path}", 
                    json=payload, 
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
            except Exception as e:
                logger.debug(f"HelmAnalytics Error: {e}")

        # Fire and forget
        threading.Thread(target=_post).start()

    def check_shield(self, payload):
        """
        Synchronous check against Helm Firewall.
        Returns (allowed: bool, reason: str)
        """
        if not self.site_id:
            return True, ""
            
        try:
            # We need to reshape payload slightly for the decision endpoint
            check_payload = {
                "siteId": payload["siteId"],
                "ip": payload["clientIp"],
                "userAgent": payload["userAgent"],
                "url": payload["url"]
            }
            
            resp = requests.post(
                f"{self.api_url}/api/shield/decision",
                json=check_payload,
                headers={'Content-Type': 'application/json'},
                timeout=2 # Fast timeout for blocking checks
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("action") == "block":
                    return False, data.get("reason", "blocked")
                    
            return True, ""
        except Exception as e:
            # If check fails, fail open (allow)
            logger.error(f"Helm Shield Error: {e}")
            return True, "error_open"

    def track(self, request, event_type="pageview", metadata=None, shield=False):
        """
        Generic track method. 
        If shield=True, this method returns False if the request should be blocked.
        """
        try:
            # 1. URL
            if hasattr(request, 'url'):
                url = str(request.url)
            else:
                url = str(request)
            
            # 2. Headers
            headers = getattr(request, 'headers', {})
            
            # 3. IP
            if hasattr(request, 'client') and hasattr(request.client, 'host'):
                ip = request.client.host
            elif hasattr(request, 'remote_addr'):
                ip = request.remote_addr
            else:
                ip = ''
            
            # Trust X-Forwarded-For
            if hasattr(headers, 'get'):
                x_fwd = headers.get('x-forwarded-for') or headers.get('X-Forwarded-For')
                if x_fwd:
                    ip = x_fwd.split(',')[0].strip()
            
            user_agent = headers.get('user-agent') if hasattr(headers, 'get') else ''
            referrer = headers.get('referer') if hasattr(headers, 'get') else ''
            
            # Session ID from header
            session_id = headers.get('x-helm-session-id') if hasattr(headers, 'get') else ''
            if not session_id and hasattr(request, 'session_id'):
                session_id = request.session_id
            
            # Fallback for dict-like headers
            if not user_agent and isinstance(headers, dict):
                 user_agent = headers.get('User-Agent', '')
            if not referrer and isinstance(headers, dict):
                 referrer = headers.get('Referer', '')
            if not session_id and isinstance(headers, dict):
                 session_id = headers.get('X-Helm-Session-Id', '')

            payload = {
                "siteId": self.site_id,
                "sessionId": session_id,
                "url": url,
                "clientIp": ip,
                "userAgent": user_agent,
                "referrer": referrer,
                "eventType": event_type,
                "screenWidth": 0,
                "isServerSide": True
            }
            if metadata:
                payload.update(metadata)
            
            # Shield Check (Blocking)
            if shield:
                allowed, reason = self.check_shield(payload)
                if not allowed:
                    logger.warning(f"[Helm Shield] Blocked IP: {ip} Reason: {reason}")
                    return False

            self._send_payload(payload, "/track")
            return True

    def track_event(self, request, event_name, properties=None):
        """
        Custom event tracking.
        """
        try:
            # URL
            if hasattr(request, 'url'):
                url = str(request.url)
            else:
                url = str(request)
            
            # Headers
            headers = getattr(request, 'headers', {})
            
            # Referrer
            referrer = headers.get('referer') if hasattr(headers, 'get') else ''
            if not referrer and isinstance(headers, dict):
                referrer = headers.get('Referer', '')

            # Session ID from header
            session_id = headers.get('x-helm-session-id') if hasattr(headers, 'get') else ''
            if not session_id and hasattr(request, 'session_id'):
                session_id = request.session_id
            if not session_id and isinstance(headers, dict):
                 session_id = headers.get('X-Helm-Session-Id', '')

            payload = {
                "siteId": self.site_id,
                "sessionId": session_id,
                "eventName": event_name,
                "properties": properties or {},
                "url": url,
                "referrer": referrer,
                "isServerSide": True
            }
            
            self._send_payload(payload, "/track/event")
            return True
        except Exception as e:
            logger.error(f"HelmAnalytics Event Tracking Failed: {e}")
            return True # Fail open
            
        except Exception as e:
            logger.error(f"HelmAnalytics Tracking Failed: {e}")
            return True # Fail open

    def flask_middleware(self, shield=False):
        from flask import request, abort
        def _track():
            if request.endpoint and 'static' not in request.endpoint:
                allowed = self.track(request, shield=shield)
                if not allowed:
                    abort(403)
        return _track

    def fastapi_dispatch(self, request, call_next):
        """
        FastAPI/Starlette dispatch function (Legacy).
        """
        return self.fastapi_middleware(shield=False)(request, call_next)

    def fastapi_middleware(self, shield=False):
        """
        Returns a dispatch function.
        Usage: app.add_middleware(BaseHTTPMiddleware, dispatch=helm.fastapi_middleware(shield=True))
        """
        from starlette.responses import PlainTextResponse
        
        async def dispatch(request, call_next):
            # Note: synchronous requests call in async function might block event loop.
            # For high performance async apps, this part of the SDK should be async/await.
            # Keeping sync for now for simplicity & compatibility.
            allowed = self.track(request, shield=shield)
            if not allowed:
                return PlainTextResponse("Forbidden by Helm Aegis", status_code=403)
                
            response = await call_next(request)
            return response
            
        return dispatch
