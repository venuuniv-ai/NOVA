import hashlib
import hmac
import json
import secrets
import time

from redis import Redis
from redis.exceptions import RedisError

from app.model_routing.contracts import ProviderResult

_SIGNING_KEY = secrets.token_bytes(
    32
)  # Per-process rotation makes old cache entries misses after restart.


class ResultCache:
    def __init__(self, url, ttl=300, prefix="nova:model-cache", signing_key=_SIGNING_KEY):
        self.client = Redis.from_url(url, socket_timeout=1, socket_connect_timeout=1)
        self.ttl = min(max(ttl, 1), 3600)
        self.prefix, self.signing_key = prefix, signing_key

    def key(self, request, spec):
        normalized = request.model_dump(mode="json", exclude={"request_id", "trace_id"})
        material = {
            "request": normalized,
            "provider": spec.model_dump(mode="json"),
            "policy": "routing-v1",
            "settings": {"temperature": 0},
            "schema": request.schema_version,
        }
        digest = hashlib.sha256(
            json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return f"{self.prefix}:{request.user_id}:{digest}"

    def get(self, key):
        try:
            raw = self.client.get(key)
            if raw is None:
                return None, "MISS"
            if len(raw) > 100000:
                return None, "ERROR"
            data = json.loads(raw)
            body = data["body"]
            if not isinstance(body, str) or not isinstance(data["signature"], str):
                return None, "ERROR"
            signature = hmac.new(self.signing_key, body.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, data["signature"]):
                return None, "ERROR"
            envelope = json.loads(body)
            if envelope["key"] != key or envelope["expires"] <= time.time():
                return None, "MISS"
            return ProviderResult.model_validate(envelope["result"]), "HIT"
        except (RedisError, ValueError, KeyError, TypeError):
            return None, "ERROR"

    def put(self, key, result):
        body = json.dumps(
            {
                "key": key,
                "expires": time.time() + self.ttl,
                "result": result.model_dump(mode="json"),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        encoded = json.dumps(
            {
                "body": body,
                "signature": hmac.new(self.signing_key, body.encode(), hashlib.sha256).hexdigest(),
            }
        )
        try:
            self.client.set(key, encoded, ex=self.ttl)
            return True
        except RedisError:
            return False
