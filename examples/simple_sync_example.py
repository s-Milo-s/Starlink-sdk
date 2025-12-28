"""
Simple synchronous example showing OpenAI-style usage of the Starlink SDK.

Before running:
export STARLINK_API_SECRET="your-api-secret"
export STARLINK_BASE_URL="https://your-api-endpoint.com"  # optional
"""

from datetime import datetime, timedelta
from starlink_sdk import StarlinkClient


def main():
    """Simple synchronous main function - no async/await needed!"""
    
    # Create client - just like OpenAI
    client = StarlinkClient()
    
    # Check API health
    print("🏥 Checking API health...")
    health_status = client.health_check()
    print(f"API Status: {health_status}")
    
    # Get fleet health - simple method call
    print("\n📊 Getting fleet health...")
    health = client.fleet.get_health(
        from_time=datetime.now() - timedelta(hours=24),
        to_time=datetime.now()
    )
    
    print(f"Fleet Status:")
    print(f"  ✅ Healthy:  {health.counts.healthy}")
    print(f"  ⚠️  Degraded: {health.counts.degraded}")
    print(f"  ❌ Offline:  {health.counts.offline}")
    
    # List terminals - clean namespace
    print(f"\n📡 Listing terminals...")
    terminals = client.terminals.list(limit=10)
    
    print(f"Found {len(terminals.items)} terminals:")
    for terminal in terminals.items:
        status_emoji = {"online": "🟢", "degraded": "🟡", "offline": "🔴"}.get(terminal.status, "⚫")
        print(f"  {status_emoji} {terminal.terminal_id} - {terminal.status}")
    
    # Get details for first terminal if available
    if terminals.items:
        terminal_id = terminals.items[0].terminal_id
        print(f"\n🔍 Getting details for {terminal_id}...")
        
        terminal_detail = client.terminals.get(terminal_id)
        print(f"  Name: {terminal_detail.name or 'Unnamed'}")
        print(f"  Health: {terminal_detail.health_status}")
        print(f"  Last seen: {terminal_detail.last_seen}")
        
        # Get metrics
        print(f"\n📊 Getting metrics...")
        metrics = client.terminals.get_metrics(
            terminal_id=terminal_id,
            from_time=datetime.now() - timedelta(hours=1),
            to_time=datetime.now(),
            metrics=["latency_ms", "downlink_mbps"]
        )
        
        print(f"  Retrieved metrics for {len(metrics.series)} metric types")
        for metric_name, data_points in metrics.series.items():
            if data_points:
                latest = data_points[-1]
                print(f"  {metric_name}: {latest.v} at {latest.t.strftime('%H:%M:%S')}")
    
    # List alerts - simple filtering
    print(f"\n🚨 Checking for critical alerts...")
    alerts = client.alerts.list(severity="critical", limit=5)
    
    if alerts.items:
        print(f"Found {len(alerts.items)} critical alerts:")
        for alert in alerts.items:
            print(f"  🚨 {alert.type} on {alert.terminal_id}")
            print(f"     {alert.message}")
    else:
        print("  ✅ No critical alerts!")
    
    print(f"\n✨ All done! No async/await required.")


if __name__ == "__main__":
    main()
