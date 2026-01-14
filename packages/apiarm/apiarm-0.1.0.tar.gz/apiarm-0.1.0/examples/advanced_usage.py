"""
Example: Advanced API-ARM Usage

Demonstrates logging, caching, and analysis features.
"""

import asyncio
from pathlib import Path
from apiarm import APIArm
from apiarm.core.analyzer import AnalysisDepth


async def main():
    """Demonstrate advanced API-ARM features."""
    
    print("=" * 60)
    print("🦾 API-ARM Advanced Usage Demo")
    print("=" * 60)
    
    # Create API-ARM with logging and caching
    async with APIArm("https://jsonplaceholder.typicode.com") as arm:
        
        # Enable features
        arm.enable_logging(console=True)
        arm.enable_caching(max_size=50, default_ttl=60)
        
        print("\n📊 Making requests with logging enabled...\n")
        
        # Make several requests
        await arm.get("/users")
        await arm.get("/posts/1")
        await arm.get("/users")  # This will be cached!
        await arm.get("/users")  # Also cached!
        
        print("\n" + "-" * 40)
        print("📈 Statistics:")
        print("-" * 40)
        
        # Show stats
        arm.print_stats()
        
        # Show cache info
        print(f"\nCache size: {arm.cache.size} entries")
        print(f"Cache hit rate: {arm.cache.hit_rate * 100:.1f}%")
        
        print("\n" + "-" * 40)
        print("📝 Request Log Details:")
        print("-" * 40)
        
        for log in arm.logger.get_logs():
            status = "✓" if log.success else "✗"
            print(f"  {status} {log.method} {log.path} - {log.response_status} ({log.duration_ms}ms)")
            
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
