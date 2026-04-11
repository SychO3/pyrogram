#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple

from pyrogram import raw

log = logging.getLogger(__name__)


class _EndpointSelector:
    """Internal selector to choose the lowest-latency DC endpoint.

    This module is intentionally internal and not user-configurable.
    """

    # Internal tuning knobs (not exposed to user API)
    CACHE_TTL_S: float = 900.0
    PROBE_TIMEOUT_S: float = 0.8
    MAX_PROBE_CANDIDATES: int = 5

    def __init__(self) -> None:
        # key -> (ip, port, monotonic_ts, latency_ms)
        self._cache: Dict[Tuple, Tuple[str, int, float, float]] = {}

    @staticmethod
    def _proxy_signature(proxy: Optional[dict]) -> Optional[Tuple]:
        if not proxy:
            return None
        return (
            proxy.get("scheme"),
            proxy.get("hostname"),
            proxy.get("port"),
            proxy.get("username"),
        )

    @staticmethod
    def _protocol_signature(protocol_factory: type) -> str:
        return getattr(protocol_factory, "__name__", str(protocol_factory))

    def _cache_key(
        self,
        dc_id: int,
        is_media: bool,
        is_cdn: bool,
        proxy: Optional[dict],
        ipv6: bool,
        protocol_factory: type,
    ) -> Tuple:
        return (
            dc_id,
            is_media,
            is_cdn,
            self._proxy_signature(proxy),
            ipv6,
            self._protocol_signature(protocol_factory),
        )

    @staticmethod
    def _deduplicate(candidates: List["raw.types.DcOption"]) -> List["raw.types.DcOption"]:
        seen = set()
        uniq: List[raw.types.DcOption] = []
        for dc in candidates:
            key = (dc.ip_address, dc.port)
            if key in seen:
                continue
            seen.add(key)
            uniq.append(dc)
        return uniq

    def _get_cached(self, key: Tuple, candidates: List["raw.types.DcOption"]) -> Optional["raw.types.DcOption"]:
        entry = self._cache.get(key)
        if not entry:
            return None
        ip, port, ts, _ = entry
        if time.monotonic() - ts > self.CACHE_TTL_S:
            return None
        for dc in candidates:
            if dc.ip_address == ip and dc.port == port:
                return dc
        return None

    async def _probe(
        self,
        protocol_factory: type,
        ip: str,
        port: int,
        ipv6: bool,
        proxy: Optional[dict],
    ) -> Optional[float]:
        start = time.perf_counter()
        protocol = protocol_factory(ipv6=ipv6, proxy=proxy, crypto_executor_workers=1)
        try:
            await asyncio.wait_for(protocol.connect((ip, port)), timeout=self.PROBE_TIMEOUT_S)
        except Exception as e:
            log.info("Endpoint probe failed: %s:%s (%s)", ip, port, e)
            try:
                await protocol.close()
            except Exception:
                pass
            return None
        else:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            try:
                await protocol.close()
            except Exception:
                pass
            log.info("Endpoint probe success: %s:%s in %.1f ms", ip, port, elapsed_ms)
            return elapsed_ms

    async def select(
        self,
        client,
        dc_id: int,
        candidates: List["raw.types.DcOption"],
        is_media: bool,
        is_cdn: bool,
        ipv6: bool,
    ) -> Optional["raw.types.DcOption"]:
        if not candidates:
            return None

        candidates = self._deduplicate(candidates)
        if not candidates:
            return None

        key = self._cache_key(dc_id, is_media, is_cdn, getattr(client, "proxy", None), ipv6, getattr(client, "protocol_factory", type))

        cached = self._get_cached(key, candidates)
        if cached is not None:
            entry = self._cache.get(key)
            latency_ms = entry[3] if entry else None
            log.info(
                "Using cached endpoint DC%s: %s:%s (%.1f ms)",
                dc_id,
                cached.ip_address,
                cached.port,
                latency_ms if latency_ms is not None else -1.0,
            )
            return cached

        # Probe all candidates
        probe_list = candidates
        log.info("Probing %s endpoints for DC%s (media=%s, cdn=%s, ipv6=%s)", len(probe_list), dc_id, is_media, is_cdn, ipv6)

        tasks = [
            asyncio.create_task(
                self._probe(
                    getattr(client, "protocol_factory", type),
                    dc.ip_address,
                    dc.port,
                    dc.ipv6,
                    getattr(client, "proxy", None),
                )
            )
            for dc in probe_list
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        best_idx = None
        best_latency = None
        for idx, res in enumerate(results):
            if isinstance(res, Exception) or res is None:
                continue
            if best_latency is None or res < best_latency:
                best_latency = res
                best_idx = idx

        if best_idx is not None:
            best = probe_list[best_idx]
            # Cache best
            self._cache[key] = (best.ip_address, best.port, time.monotonic(), float(best_latency))
            log.info("Selected endpoint DC%s: %s:%s (%.1f ms)", dc_id, best.ip_address, best.port, best_latency)
            return best

        # Fallback to first candidate if all probes failed
        fallback = candidates[0]
        log.info(
            "Endpoint probing failed for DC%s, falling back to %s:%s",
            dc_id,
            fallback.ip_address,
            fallback.port,
        )
        # Do not cache failures; next call may try again
        return fallback


_SELECTOR = _EndpointSelector()


async def select_best_dc_option(
    client,
    dc_id: int,
    candidates: List["raw.types.DcOption"],
    *,
    is_media: bool,
    is_cdn: bool,
    ipv6: bool,
) -> Optional["raw.types.DcOption"]:
    return await _SELECTOR.select(client, dc_id, candidates, is_media, is_cdn, ipv6)


