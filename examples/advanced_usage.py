"""
Advanced example showing error handling, custom configuration, and batch operations.

Before running:
export STARLINK_API_SECRET="your-api-secret"
export STARLINK_BASE_URL="https://your-api-endpoint.com"  # optional
"""

import asyncio
import httpx
from datetime import datetime, timedelta
from typing import List

from starlink_sdk import (
    StarlinkClient,
    StarlinkAPIError,
    StarlinkClientError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    TerminalSummary,
    create_pagination_helper
)


async def error_handling_example(client: StarlinkClient):
    """Example of comprehensive error handling."""
    print("⚠️ Error Handling Examples...")
    
    # Test different error scenarios
    error_scenarios = [
        ("Invalid terminal ID", lambda: client.get_terminal_detail("INVALID_TERMINAL")),
        ("Invalid date range", lambda: client.get_fleet_health(
            from_time=datetime.now(),
            to_time=datetime.now() - timedelta(hours=1)  # Invalid: end before start
        )),
        ("Non-existent metrics", lambda: client.get_terminal_metrics(
            terminal_id="INVALID_TERMINAL",
            from_time=datetime.now() - timedelta(hours=1),
            to_time=datetime.now(),
            metrics=["invalid_metric"]
        ))
    ]
    
    for description, operation in error_scenarios:
        print(f"\n🧪 Testing: {description}")
        try:
            await operation()
            print("  ✅ Operation succeeded (unexpected)")
        except NotFoundError as e:
            print(f"  🔍 Not found error: {e.message}")
        except ValidationError as e:
            print(f"  📝 Validation error: {e.message}")
            if e.detail:
                print(f"     Details: {e.detail}")
        except AuthenticationError as e:
            print(f"  🔐 Auth error: {e.message}")
        except RateLimitError as e:
            print(f"  🚦 Rate limit error: {e.message}")
            if e.retry_after:
                print(f"     Retry after: {e.retry_after} seconds")
        except StarlinkAPIError as e:
            print(f"  🌐 API error {e.status_code}: {e.message}")
        except StarlinkClientError as e:
            print(f"  💻 Client error: {e.message}")
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")


async def custom_client_example():
    """Example of using custom HTTP client configuration."""
    print("\n🔧 Custom Client Configuration...")
    
    # Create custom HTTP client with specific settings
    custom_httpx_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, read=60.0),  # 30s connect, 60s read
        limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
        headers={"User-Agent": "StarLink-SDK-Example/1.0"}
    )
    
    try:
        async with StarlinkClient(
            client=custom_httpx_client,
            max_retries=5
        ) as client:
            print("  ✅ Custom client created successfully")
            
            # Test the custom client
            health = await client.health_check()
            print(f"  🏥 Health check with custom client: {health}")
            
    except Exception as e:
        print(f"  ❌ Custom client error: {e}")
    finally:
        await custom_httpx_client.aclose()


async def batch_operations_example(client: StarlinkClient):
    """Example of batch operations and parallel processing."""
    print("\n🔄 Batch Operations Example...")
    
    # Get list of terminals first
    terminals_response = await client.list_terminals(limit=5)
    terminal_ids = [t.terminal_id for t in terminals_response.items]
    
    if not terminal_ids:
        print("  ⚠️ No terminals available for batch operations")
        return
    
    print(f"  📡 Processing {len(terminal_ids)} terminals in parallel...")
    
    # Batch get terminal details (parallel)
    async def get_terminal_detail_safe(terminal_id: str):
        try:
            return await client.get_terminal_detail(terminal_id)
        except Exception as e:
            print(f"    ❌ Error getting details for {terminal_id}: {e}")
            return None
    
    # Execute in parallel
    start_time = datetime.now()
    terminal_details = await asyncio.gather(
        *[get_terminal_detail_safe(tid) for tid in terminal_ids],
        return_exceptions=True
    )
    duration = datetime.now() - start_time
    
    successful_details = [d for d in terminal_details if d is not None]
    print(f"  ✅ Retrieved details for {len(successful_details)}/{len(terminal_ids)} terminals")
    print(f"  ⏱️ Total time: {duration.total_seconds():.2f} seconds")
    
    # Batch get metrics for successful terminals
    if successful_details:
        print(f"\n📊 Getting metrics for terminals...")
        
        async def get_metrics_safe(terminal_id: str):
            try:
                return await client.get_terminal_metrics(
                    terminal_id=terminal_id,
                    from_time=datetime.now() - timedelta(hours=1),
                    to_time=datetime.now(),
                    metrics=["latency_ms", "downlink_mbps"]
                )
            except Exception as e:
                print(f"    ❌ Error getting metrics for {terminal_id}: {e}")
                return None
        
        metrics_results = await asyncio.gather(
            *[get_metrics_safe(d.terminal_id) for d in successful_details],
            return_exceptions=True
        )
        
        successful_metrics = [m for m in metrics_results if m is not None]
        print(f"  📈 Retrieved metrics for {len(successful_metrics)} terminals")


async def pagination_helper_example(client: StarlinkClient):
    """Example using pagination helper for large datasets."""
    print("\n📚 Pagination Helper Example...")
    
    # Create pagination helper for terminals
    paginator = create_pagination_helper(
        client,
        'list_terminals',
        limit=10  # Small page size for demo
    )
    
    all_terminals: List[TerminalSummary] = []
    page_count = 0
    
    print("  📄 Fetching all terminals using pagination helper...")
    
    while paginator.has_more and page_count < 5:  # Limit to 5 pages for demo
        page = await paginator.get_next_page()
        if page:
            all_terminals.extend(page.items)
            page_count += 1
            print(f"    Page {page_count}: {len(page.items)} terminals")
        else:
            break
    
    print(f"  ✅ Total terminals collected: {len(all_terminals)}")
    
    # Show summary by status
    status_counts = {}
    for terminal in all_terminals:
        status = terminal.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("  📊 Terminal status summary:")
    for status, count in status_counts.items():
        print(f"    {status}: {count}")


async def main():
    """Main example function."""
    try:
        async with StarlinkClient(timeout=30.0, max_retries=3) as client:
            await error_handling_example(client)
            await batch_operations_example(client)
            await pagination_helper_example(client)
        
        # Test custom client configuration separately
        await custom_client_example()
        
    except Exception as e:
        print(f"💥 Unexpected error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
