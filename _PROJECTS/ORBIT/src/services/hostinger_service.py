"""
Hostinger VPS Service
Calls the Hostinger REST API to fetch real-time VPS metrics.

No scraping needed — Hostinger provides an official API.
Auth: Bearer token from Hostinger panel → Settings → API.
API base: https://api.hostinger.com/v1/vps/
"""

import aiohttp
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
import statistics

from loguru import logger


HOSTINGER_API_BASE = "https://api.hostinger.com/v1/vps"
_TIMEOUT = aiohttp.ClientTimeout(total=15)


@dataclass
class VpsMetricsSnapshot:
    """Current VPS health snapshot."""
    vps_id: int
    hostname: str
    state: str               # "running" | "stopped" | ...

    # Resource usage (latest sample)
    cpu_pct: float           # 0-100
    ram_pct: float           # 0-100
    ram_used_gb: float
    ram_total_gb: float
    disk_pct: float          # 0-100
    disk_used_gb: float
    disk_total_gb: float

    # Averages over the last 2h
    cpu_avg_2h: float
    ram_avg_2h: float

    # Uptime
    uptime_seconds: int
    uptime_human: str        # "37d 12h"

    # Network (last sample, bytes)
    net_out_bytes: int
    net_in_bytes: int

    # Plan info
    plan: str
    cpus: int
    memory_gb: float
    disk_gb: float
    ipv4: str

    fetched_at: str


def _bytes_to_gb(b: float) -> float:
    return round(b / (1024 ** 3), 1)


def _uptime_human(seconds: int) -> str:
    d = seconds // 86400
    h = (seconds % 86400) // 3600
    m = (seconds % 3600) // 60
    if d > 0:
        return f"{d}d {h}h"
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"


def _latest(usage_dict: dict) -> float:
    """Return value of the highest-timestamp key."""
    if not usage_dict:
        return 0.0
    return usage_dict[max(usage_dict, key=int)]


def _avg(usage_dict: dict) -> float:
    """Return mean of all values."""
    if not usage_dict:
        return 0.0
    return statistics.mean(usage_dict.values())


async def get_vps_metrics(api_token: str, vps_id: int) -> Optional[VpsMetricsSnapshot]:
    """
    Fetch current VPS metrics from Hostinger API.
    Pulls last 2h of data and returns the latest sample + 2h averages.

    Args:
        api_token: Hostinger API Bearer token
        vps_id: VM ID (visible in hPanel URL or via list endpoint)

    Returns:
        VpsMetricsSnapshot or None if the API call fails
    """
    now = datetime.now(tz=timezone.utc)
    date_from = (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_to = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
    }

    async with aiohttp.ClientSession(headers=headers, timeout=_TIMEOUT) as session:
        # Fetch VM details (plan, hostname, state)
        try:
            async with session.get(f"{HOSTINGER_API_BASE}/virtual-machines/{vps_id}") as r:
                if r.status != 200:
                    logger.warning(f"Hostinger VM details returned {r.status}")
                    vm_data = {}
                else:
                    vm_data = await r.json()
        except Exception as e:
            logger.error(f"Hostinger VM details error: {e}")
            vm_data = {}

        # Fetch metrics
        try:
            params = {"date_from": date_from, "date_to": date_to}
            async with session.get(
                f"{HOSTINGER_API_BASE}/virtual-machines/{vps_id}/metrics",
                params=params
            ) as r:
                if r.status != 200:
                    body = await r.text()
                    logger.error(f"Hostinger metrics returned {r.status}: {body[:200]}")
                    return None
                metrics_data = await r.json()
        except Exception as e:
            logger.error(f"Hostinger metrics error: {e}")
            return None

    # ── Parse VM info ──────────────────────────────────────────────────────
    plan = vm_data.get("plan", "unknown")
    hostname = vm_data.get("hostname", f"vm-{vps_id}")
    state = vm_data.get("state", "unknown")
    cpus = vm_data.get("cpus", 0)
    mem_mb = vm_data.get("memory", 0)
    disk_mb = vm_data.get("disk", 0)
    ipv4_list = vm_data.get("ipv4", [])
    ipv4 = ipv4_list[0].get("address", "") if ipv4_list else ""

    ram_total_gb = _bytes_to_gb(mem_mb * 1024 * 1024) if mem_mb else 8.0
    disk_total_gb = _bytes_to_gb(disk_mb * 1024 * 1024) if disk_mb else 100.0

    # ── Parse metrics ──────────────────────────────────────────────────────
    cpu_usage = metrics_data.get("cpu_usage", {}).get("usage", {})
    ram_usage = metrics_data.get("ram_usage", {}).get("usage", {})
    disk_usage = metrics_data.get("disk_space", {}).get("usage", {})
    net_out = metrics_data.get("outgoing_traffic", {}).get("usage", {})
    net_in = metrics_data.get("incoming_traffic", {}).get("usage", {})
    uptime_data = metrics_data.get("uptime", {}).get("usage", {})

    cpu_latest = _latest(cpu_usage)
    ram_latest_bytes = _latest(ram_usage)
    disk_latest_bytes = _latest(disk_usage)
    uptime_secs = int(_latest(uptime_data))

    ram_used_gb = _bytes_to_gb(ram_latest_bytes)
    disk_used_gb = _bytes_to_gb(disk_latest_bytes)

    # Use plan values if available, fallback to metric ratios
    if mem_mb:
        ram_total_gb_precise = mem_mb / 1024
        ram_pct = round(ram_latest_bytes / (mem_mb * 1024 * 1024) * 100, 1)
    else:
        ram_total_gb_precise = ram_total_gb
        ram_pct = 0.0

    if disk_mb:
        disk_pct = round(disk_latest_bytes / (disk_mb * 1024 * 1024) * 100, 1)
    else:
        disk_pct = 0.0

    cpu_avg = round(_avg(cpu_usage), 1)
    ram_bytes_avg = _avg(ram_usage)
    ram_avg_pct = round(ram_bytes_avg / (mem_mb * 1024 * 1024) * 100, 1) if mem_mb else 0.0

    return VpsMetricsSnapshot(
        vps_id=vps_id,
        hostname=hostname,
        state=state,
        cpu_pct=round(cpu_latest, 1),
        ram_pct=ram_pct,
        ram_used_gb=ram_used_gb,
        ram_total_gb=round(ram_total_gb_precise, 1),
        disk_pct=disk_pct,
        disk_used_gb=disk_used_gb,
        disk_total_gb=round(disk_total_gb, 1),
        cpu_avg_2h=cpu_avg,
        ram_avg_2h=ram_avg_pct,
        uptime_seconds=uptime_secs,
        uptime_human=_uptime_human(uptime_secs),
        net_out_bytes=int(_latest(net_out)),
        net_in_bytes=int(_latest(net_in)),
        plan=plan,
        cpus=cpus,
        memory_gb=round(ram_total_gb_precise, 1),
        disk_gb=round(disk_total_gb, 1),
        ipv4=ipv4,
        fetched_at=now.isoformat(),
    )


async def list_vps(api_token: str) -> list[dict]:
    """List all VPS instances for this Hostinger account."""
    headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}
    async with aiohttp.ClientSession(headers=headers, timeout=_TIMEOUT) as session:
        try:
            async with session.get(f"{HOSTINGER_API_BASE}/virtual-machines") as r:
                if r.status != 200:
                    logger.error(f"Hostinger list VMs returned {r.status}")
                    return []
                data = await r.json()
                return data if isinstance(data, list) else data.get("data", [])
        except Exception as e:
            logger.error(f"Hostinger list VMs error: {e}")
            return []
