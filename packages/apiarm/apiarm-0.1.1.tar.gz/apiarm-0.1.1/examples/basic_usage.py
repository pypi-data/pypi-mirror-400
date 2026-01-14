"""
Example: Basic API-ARM Usage

This example demonstrates how to use API-ARM to analyze and
make requests to a public API.
"""

import asyncio
from apiarm import APIArm
from apiarm.core.analyzer import AnalysisDepth
from apiarm.models.endpoint import HTTPMethod


async def main():
    """Main example function."""
    
    # Example 1: Basic API Analysis
    print("=" * 60)
    print("Example 1: Analyzing JSONPlaceholder API")
    print("=" * 60)
    
    async with APIArm("https://jsonplaceholder.typicode.com") as arm:
        # Analyze the API
        analysis = await arm.analyze(depth=AnalysisDepth.STANDARD)
        
        print(f"Base URL: {analysis.base_url}")
        print(f"API Version: {analysis.api_version or 'Not detected'}")
        print(f"Auth Methods: {[am.value for am in analysis.auth_methods]}")
        print(f"Endpoints found: {analysis.endpoint_count}")
        
    # Example 2: Making Requests
    print("\n" + "=" * 60)
    print("Example 2: Making GET Request")
    print("=" * 60)
    
    async with APIArm("https://jsonplaceholder.typicode.com") as arm:
        # Get a list of users
        response = await arm.get("/users")
        
        print(f"Status: {response.status_code}")
        print(f"Success: {response.success}")
        
        if response.success and response.data:
            print(f"Users found: {len(response.data)}")
            print(f"First user: {response.data[0]['name']}")
            
    # Example 3: POST Request
    print("\n" + "=" * 60)
    print("Example 3: Making POST Request")
    print("=" * 60)
    
    async with APIArm("https://jsonplaceholder.typicode.com") as arm:
        # Create a new post
        new_post = {
            "title": "API-ARM Test Post",
            "body": "This is a test post created by API-ARM",
            "userId": 1,
        }
        
        response = await arm.post("/posts", json_body=new_post)
        
        print(f"Status: {response.status_code}")
        print(f"Created post ID: {response.get('id')}")
        print(f"Title: {response.get('title')}")
        
    # Example 4: Using Authentication
    print("\n" + "=" * 60)
    print("Example 4: With API Key Authentication")
    print("=" * 60)
    
    async with APIArm("https://api.example.com") as arm:
        # Configure API key authentication
        arm.set_api_key("your-api-key-here", header_name="X-API-Key")
        
        # Now all requests will include the API key header
        # response = await arm.get("/protected-endpoint")
        print("API key configured (example only, no actual request made)")
        
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
