"""
Example showing terminal management operations including listing, details, and metrics.

Before running:
export STARLINK_API_SECRET="your-api-secret"
export STARLINK_BASE_URL="https://your-api-endpoint.com"  # optional
"""

import asyncio
from datetime import datetime, timedelta

from starlink_sdk import StarlinkClient, TerminalStatus, Interval


async def list_terminals_example(client: StarlinkClient):
    """Example of listing terminals with filtering."""
    print("📡 Listing terminals...")
    
    # Get all terminals (first page)
    all_terminals = await client.list_terminals(limit=10)
    print(f"Found {len(all_terminals.items)} terminals (showing first 10)")
    
    for terminal in all_terminals.items:
        status_emoji = {
            TerminalStatus.ONLINE: "🟢",
            TerminalStatus.DEGRADED: "🟡", 
            TerminalStatus.OFFLINE: "🔴"
        }.get(terminal.status, "⚫")
        
        location_str = ""
        if terminal.location and terminal.location.lat and terminal.location.lon:
            location_str = f" @ {terminal.location.lat:.2f}, {terminal.location.lon:.2f}"
        
        print(f"  {status_emoji} {terminal.terminal_id} ({terminal.name or 'Unnamed'})")
        print(f"     Status: {terminal.status} | Health: {terminal.health_status}")
        print(f"     Last seen: {terminal.last_seen}{location_str}")
    
    # Filter by status
    print(f"\n🟢 Looking for online terminals only...")
    online_terminals = await client.list_terminals(
        status=TerminalStatus.ONLINE,
        limit=5
    )
    print(f"Found {len(online_terminals.items)} online terminals")
    
    return online_terminals.items


async def terminal_details_example(client: StarlinkClient, terminal_id: str):
    """Example of getting detailed terminal information."""
    print(f"\n🔍 Getting details for terminal {terminal_id}...")
    
    try:
        terminal = await client.get_terminal_detail(terminal_id)
        
        print(f"📋 Terminal Details:")
        print(f"  ID: {terminal.terminal_id}")
        print(f"  Name: {terminal.name or 'Unnamed'}")
        print(f"  Status: {terminal.status}")
        print(f"  Health: {terminal.health_status}")
        print(f"  Last seen: {terminal.last_seen}")
        print(f"  Firmware: {terminal.firmware_version or 'Unknown'}")
        print(f"  Account: {terminal.account_id or 'Unknown'}")
        
        if terminal.location:
            loc = terminal.location
            print(f"  Location: {loc.label or 'Unlabeled'}")
            if loc.lat and loc.lon:
                print(f"    Coordinates: {loc.lat:.6f}, {loc.lon:.6f}")
        
        if terminal.health_factors:
            print(f"  🏥 Health Factors:")
            for factor in terminal.health_factors:
                status = "✅" if factor.value <= factor.threshold else "❌"
                print(f"    {status} {factor.factor}: {factor.value} (threshold: {factor.threshold})")
                print(f"       {factor.message}")
    
    except Exception as e:
        print(f"❌ Error getting terminal details: {e}")


async def terminal_metrics_example(client: StarlinkClient, terminal_id: str):
    """Example of getting terminal metrics."""
    print(f"\n📊 Getting metrics for terminal {terminal_id}...")
    
    try:
        # Get last 6 hours of metrics
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=6)
        
        metrics = await client.get_terminal_metrics(
            terminal_id=terminal_id,
            from_time=start_time,
            to_time=end_time,
            interval=Interval.FIVE_MINUTES,
            metrics=["latency_ms", "packet_loss_pct", "downlink_mbps", "uplink_mbps"]
        )
        
        print(f"📈 Metrics Summary ({start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}):")
        
        for metric_name, data_points in metrics.series.items():
            if not data_points:
                continue
            
            latest = data_points[-1]
            avg_value = sum(p.v for p in data_points) / len(data_points)
            
            unit = {
                "latency_ms": "ms",
                "packet_loss_pct": "%", 
                "downlink_mbps": "Mbps",
                "uplink_mbps": "Mbps"
            }.get(metric_name, "")
            
            print(f"  📊 {metric_name.replace('_', ' ').title()}:")
            print(f"     Latest: {latest.v}{unit} at {latest.t.strftime('%H:%M:%S')}")
            print(f"     Average: {avg_value:.2f}{unit} ({len(data_points)} points)")
    
    except Exception as e:
        print(f"❌ Error getting terminal metrics: {e}")


async def main():
    """Main example function."""
    async with StarlinkClient() as client:
        # List terminals
        terminals = await list_terminals_example(client)
        
        # If we have terminals, get details for the first one
        if terminals:
            terminal_id = terminals[0].terminal_id
            await terminal_details_example(client, terminal_id)
            await terminal_metrics_example(client, terminal_id)
        else:
            print("No terminals found to demonstrate details/metrics")


if __name__ == "__main__":
    asyncio.run(main())
