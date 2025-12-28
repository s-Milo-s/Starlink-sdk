"""
Example showing alert management and telemetry ingestion.

Before running:
export STARLINK_API_SECRET="your-api-secret"
export STARLINK_BASE_URL="https://your-api-endpoint.com"  # optional
"""

import asyncio
from datetime import datetime, timedelta

from starlink_sdk import (
    StarlinkClient,
    AlertStatus,
    AlertSeverity, 
    TelemetryIngestRequest,
    generate_idempotency_key
)


async def alerts_example(client: StarlinkClient):
    """Example of managing alerts."""
    print("🚨 Managing Alerts...")
    
    # Get open alerts
    print("\n📋 Open alerts:")
    open_alerts = await client.list_alerts(
        status=AlertStatus.OPEN,
        limit=10
    )
    
    if open_alerts.items:
        for alert in open_alerts.items:
            severity_emoji = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARN: "⚠️",
                AlertSeverity.CRITICAL: "🚨"
            }.get(alert.severity, "❓")
            
            print(f"  {severity_emoji} [{alert.severity.upper()}] {alert.type}")
            print(f"     Terminal: {alert.terminal_id}")
            print(f"     Message: {alert.message}")
            print(f"     Created: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("  ✅ No open alerts!")
    
    # Get critical alerts from last 7 days
    print(f"\n🚨 Critical alerts from last week:")
    week_ago = datetime.now() - timedelta(days=7)
    critical_alerts = await client.list_alerts(
        severity=AlertSeverity.CRITICAL,
        from_time=week_ago,
        limit=5
    )
    
    if critical_alerts.items:
        for alert in critical_alerts.items:
            print(f"  🚨 {alert.type} on {alert.terminal_id}")
            print(f"     {alert.message}")
            print(f"     Status: {alert.status} | Created: {alert.created_at.strftime('%m/%d %H:%M')}")
    else:
        print("  ✅ No critical alerts in the last week!")
    
    return open_alerts.items


async def telemetry_example(client: StarlinkClient, terminal_id: str):
    """Example of ingesting telemetry data."""
    print(f"\n📡 Ingesting telemetry for terminal {terminal_id}...")
    
    try:
        # Simulate some telemetry data
        telemetry = TelemetryIngestRequest(
            terminal_id=terminal_id,
            timestamp=datetime.now(),
            metrics={
                "latency_ms": 42.5,
                "packet_loss_pct": 0.05,
                "downlink_mbps": 145.2,
                "uplink_mbps": 28.7,
                "signal_strength_dbm": -72.3,
                "temperature_celsius": 35.5,
                "uptime_seconds": 86400,
                "cpu_usage_pct": 15.2,
                "memory_usage_pct": 42.1
            }
        )
        
        # Generate unique idempotency key
        idempotency_key = generate_idempotency_key()
        
        response = await client.ingest_telemetry(
            request=telemetry,
            idempotency_key=idempotency_key
        )
        
        print(f"📊 Telemetry Response:")
        print(f"  ✅ Accepted: {response.accepted}")
        print(f"  🆔 Request ID: {response.request_id}")
        print(f"  🔑 Idempotency Key: {idempotency_key}")
        
        # Show what we sent
        print(f"  📈 Metrics sent:")
        for key, value in telemetry.metrics.items():
            print(f"     {key}: {value}")
    
    except Exception as e:
        print(f"❌ Error ingesting telemetry: {e}")


async def pagination_example(client: StarlinkClient):
    """Example of handling pagination."""
    print(f"\n📖 Pagination Example...")
    
    # Get alerts with pagination
    print("Getting alerts with manual pagination:")
    page_count = 0
    total_alerts = 0
    cursor = None
    
    while page_count < 3:  # Limit to 3 pages for demo
        alerts_page = await client.list_alerts(
            limit=5,
            cursor=cursor
        )
        
        page_count += 1
        total_alerts += len(alerts_page.items)
        
        print(f"  📄 Page {page_count}: {len(alerts_page.items)} alerts")
        
        for alert in alerts_page.items:
            print(f"    • {alert.type} on {alert.terminal_id}")
        
        # Check if there are more pages
        cursor = alerts_page.next_cursor
        if not cursor:
            print("  ✅ No more pages")
            break
    
    print(f"📊 Total alerts processed: {total_alerts} across {page_count} pages")


async def main():
    """Main example function."""
    async with StarlinkClient() as client:
        # Demonstrate alerts
        alerts = await alerts_example(client)
        
        # Demonstrate telemetry ingestion
        # Use first alert's terminal ID, or a sample ID
        terminal_id = alerts[0].terminal_id if alerts else "SAMPLE_TERMINAL_123"
        await telemetry_example(client, terminal_id)
        
        # Demonstrate pagination
        await pagination_example(client)


if __name__ == "__main__":
    asyncio.run(main())
