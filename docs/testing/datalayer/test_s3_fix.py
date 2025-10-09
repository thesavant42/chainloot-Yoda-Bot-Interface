#!/usr/bin/env python3
"""
Test script to verify our FixedS3StorageClient works correctly
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test our custom S3 storage client
from lib.custom_s3_storage import FixedS3StorageClient

async def test_s3_client():
    """Test the FixedS3StorageClient initialization and close methods"""
    
    print("Testing FixedS3StorageClient...")
    
    try:
        # Initialize the client with the same parameters as in app.py
        print("1. Creating FixedS3StorageClient...")
        client = FixedS3StorageClient(bucket="my-bucket")
        print("   ✓ Client created successfully")
        
        # Test that it has all the expected attributes
        print("2. Checking client attributes...")
        print(f"   - bucket: {client.bucket}")
        print(f"   - client type: {type(client.client)}")
        print("   ✓ Attributes look good")
        
        # Test the close method (this is where the original bug was)
        print("3. Testing close method...")
        await client.close()
        print("   ✓ Close method completed successfully!")
        
        print("\n🎉 All tests passed! The FixedS3StorageClient is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("S3 Storage Client Test")
    print("=" * 50)
    
    # Run the async test
    success = asyncio.run(test_s3_client())
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")