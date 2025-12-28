"""
Basic example showing how to use the Starlink SDK to get fleet health information.

Before running:
export STARLINK_API_SECRET="your-api-secret"
export STARLINK_BASE_URL="https://your-api-endpoint.com"  # optional
"""

import asyncio
from datetime import datetime, timedelta

from starlink_sdk import StarlinkClient


async def main():
    """Main example function."""
    async with StarlinkClient() as client:
        # Check API health
        print("🏥 Checking API health...")
        health_status = await client.health_check()
        print(f"API Status: {health_status}")
        
        # Get fleet health for the last 24 hours
        print("\n📊 Getting fleet health overview...")
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        fleet_health = await client.get_fleet_health(
            from_time=start_time,
            to_time=end_time
        )
        
        print(f"📈 Fleet Health Summary ({start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}):")
        print(f"  ✅ Healthy:  {fleet_health.counts.healthy}")
        print(f"  ⚠️  Degraded: {fleet_health.counts.degraded}")
        print(f"  ❌ Offline:  {fleet_health.counts.offline}")
        
        if fleet_health.top_issues:
            print(f"\n🚨 Top Issues:")
            for issue in fleet_health.top_issues:
                print(f"  • {issue.type}: {issue.count} terminals affected")
                print(f"    Message: {issue.message}")
        else:
            print("\n✨ No major issues detected!")


if __name__ == "__main__":
    asyncio.run(main())
