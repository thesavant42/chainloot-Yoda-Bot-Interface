# CHANGELOG

## Status
# Chainlit S3 Storage Client Fix - Changelog

## Installation Directory Reorganization - October 19, 2025

**Status**: **COMPLETED**

### Changes Made

#### Task 1: Requirements Files Modularization
- **Removed**: Monolithic `requirements.txt` file from project root
- **Created**: Modular requirements files in `install/` directory:
  - `install/requirements-base.txt` - Core packages shared by all containers
  - `install/requirements-chainlit.txt` - Chainlit-specific packages
  - `install/requirements-tts-webui.txt` - TTS-WebUI-specific packages
- **Updated Dockerfiles**: Both `install/docker/Dockerfile` and `install/docker/TTS-WebUI.Dockerfile` now use appropriate requirements files
- **Benefits**: Eliminates package conflicts, reduces container sizes, prevents unnecessary package installations

#### Task 2: Docker Directory Relocation
- **Moved**: `docker/` folder from root → `install/docker/`
- **Updated**: All docker-compose references throughout codebase to use `install/docker/docker-compose.yml`
- **Updated**: Dockerfile references in docker-compose.yml to use `install/docker/Dockerfile`
- **Benefits**: Consolidates all installation-related files in one location

#### Task 3: LocalStack Initialization Relocation
- **Moved**: `localstack-init/` folder from root → `install/localstack-init/`
- **Updated**: Volume mount in `install/docker/docker-compose.yml` to reference new path
- **Updated**: All documentation references to point to new location
- **Benefits**: Groups all installation and initialization files together

#### Task 5: Database Directory Relocation
- **Moved**: `database/` folder from root → `install/database/`
- **Updated**: `start.sh` script to reference `install/database/schema.prisma`
- **Updated**: All documentation references to point to new location
- **Benefits**: Consolidates all installation/setup files in install directory

### Benefits
- **Unified Installation Structure**: All installation-related files now reside in `install/` directory
- **Modular Dependencies**: Service-specific requirements prevent cross-contamination
- **Cleaner Root Directory**: Reduced clutter and improved project organization
- **Improved Maintainability**: Easier to find and manage installation components
- **Better Docker Builds**: Smaller, more efficient containers with only necessary packages

### Files Affected
- **Removed**: `requirements.txt` (monolithic requirements file)
- **Moved**: `docker/` → `install/docker/`
- **Moved**: `localstack-init/` → `install/localstack-init/`
- **Moved**: `database/` → `install/database/`
- **Created**: `install/requirements-base.txt`, `install/requirements-chainlit.txt`, `install/requirements-tts-webui.txt`
- **Updated**: `install/docker/Dockerfile` - Uses modular requirements
- **Updated**: `install/docker/TTS-WebUI.Dockerfile` - Uses modular requirements
- **Updated**: `install/docker/docker-compose.yml` - Updated paths and dockerfile references
- **Updated**: `start.sh` - Prisma commands now use `install/database/schema.prisma`
- **Updated**: `install/database/README.md` - All command examples updated
- **Updated**: `README.md` - All docker-compose commands updated
- **Updated**: `install/docker/README.md` - All examples updated
- **Updated**: `.github/copilot-instructions.md` - File paths and commands updated
- **Updated**: `CHANGELOG.md` - Historical references updated
- **Updated**: `.dockerignore` - Updated ignore paths
- **Updated**: Multiple documentation files in `docs/` directory
- **Updated**: All references throughout codebase

---

## Project Structure Reorganization - October 16, 2025

**Status**: **COMPLETED**

### Changes Made

#### Task 1: Docker Files Cleanup
- **Moved Files**: `docker-compose.yml`, `Dockerfile` moved to `install/docker/` folder
- **Created Documentation**: Added comprehensive `install/docker/README.md` with setup and usage instructions
- **Updated References**: All documentation and scripts updated to use new paths
- **Build Verification**: Docker builds and services start correctly with new structure

#### Task 2: Database Files Cleanup
- **Moved Files**: `schema.prisma`, `migrations/`, `prisma/` moved to `install/database/` folder
- **Updated Scripts**: `start.sh` updated to use `install/database/schema.prisma` for Prisma commands
- **Docker Configuration**: Updated `install/docker/docker-compose.yml` with proper `DATABASE_URL` for Docker networking
- **Created Documentation**: Added comprehensive `install/database/README.md` with setup and usage instructions
- **Testing Verified**: Database migrations run successfully, Prisma client generates correctly, Chainlit application starts properly

#### Task 3: Config Folder Cleanup
- **Moved Files**: `config.json`, `mcp_servers.json`, `mcp_proxy_servers.json` moved to `config/` folder
- **Updated Code References**: All Python files updated to use new config paths
- **Config Loading**: `lib/config_handler.py` updated to load from `config/config.json`
- **Settings Persistence**: `app.py` config_path updated to save to `config/config.json`
- **MCP Configuration**: All MCP server config references updated to `config/mcp_servers.json`
- **Created Documentation**: Added comprehensive `config/README.md` with file descriptions and usage guidelines
- **Testing Verified**: Config loading, saving, and persistence across restarts all working correctly

#### Task 4: Documentation Updates
- **README.md**: Updated Docker setup instructions to reference `install/docker/docker-compose.yml`
- **CHANGELOG.md**: Added this entry documenting the reorganization
- **Copilot Instructions**: Updated `.github/copilot-instructions.md` with new file paths

### Benefits
- **Cleaner Root Directory**: Reduced clutter in project root
- **Better Organization**: Related files grouped logically
- **Improved Maintainability**: Easier to find and manage related components
- **Documentation**: Comprehensive READMEs for each organized folder

### Files Affected
- **Moved**: `docker-compose.yml` → `install/docker/docker-compose.yml`
- **Moved**: `Dockerfile` → `install/docker/Dockerfile`
- **Moved**: `schema.prisma` → `install/database/schema.prisma`
- **Moved**: `migrations/` → `install/database/migrations/`
- **Moved**: `prisma/` → `install/database/prisma/`
- **Moved**: `config.json` → `config/config.json`
- **Moved**: `mcp_servers.json` → `config/mcp_servers.json`
- **Moved**: `mcp_proxy_servers.json` → `config/mcp_proxy_servers.json`
- **Updated**: `start.sh` - Prisma commands now use `install/database/schema.prisma`
- **Updated**: `install/docker/docker-compose.yml` - Added DATABASE_URL for Docker networking
- **Updated**: `lib/config_handler.py` - Config loading path updated
- **Updated**: `app.py` - Config saving path updated
- **Updated**: `lib/mcp_tool_processor.py` - MCP config path updated
- **Updated**: `lib/dynamic_mcp_manager.py` - MCP config path updated
- **Created**: `install/docker/README.md` - Docker setup documentation
- **Created**: `install/database/README.md` - Database setup documentation
- **Created**: `config/README.md` - Configuration files documentation
- **Updated**: `README.md` - Docker commands reference new paths
- **Updated**: `CHANGELOG.md` - Added this reorganization entry
- **Updated**: `.github/copilot-instructions.md` - Updated file paths

---

## Issue: Application Crash on Shutdown with S3 Storage

## Issue: Application Crash on Shutdown with S3 Storage

**Date**: October 8, 2025  
**Severity**: High - Application crashes on every shutdown  
**Status**:  **RESOLVED**

---

## Problem Description

### The Error
When using Chainlit with S3 storage (via environment variables), the application would crash every time it tried to shut down, producing this error:

```
TypeError: object NoneType can't be used in 'await' expression
ERROR:    Application shutdown failed. Exiting.
```

### Root Cause Analysis

The issue was in Chainlit's built-in `S3StorageClient` class (located in `chainlit.data.storage_clients.s3`). The problem occurred in the `close()` method:

```python
async def close(self) -> None:
    await self.client.close()  # This line caused the crash
```

**Why it failed:**
1. The `self.client` is a **boto3 S3 client** (synchronous)
2. Boto3 clients **do not have an async `close()` method**
3. `self.client.close()` returns `None` (not an awaitable)
4. Attempting `await None` throws `TypeError: object NoneType can't be used in 'await' expression`

### Impact
-  Application crashes on every shutdown (Ctrl+C, browser close, user disconnect)
-  Ungraceful termination prevents proper cleanup
-  Error messages clutter logs and confuse users
-  Potential data loss in edge cases

---

## Solution Implemented

### 1. Created Custom Storage Client (`lib/custom_s3_storage.py`)

We created `FixedS3StorageClient` that inherits from the original `S3StorageClient` but overrides the problematic `close()` method:

```python
class FixedS3StorageClient(S3StorageClient):
    """
    Custom S3StorageClient that fixes the close() method issue.
    """

    async def close(self) -> None:
        """
        Properly close the S3 client without trying to await a non-async method.
        """
        try:
            logger.info("FixedS3StorageClient closing - client will be garbage collected")
            
            # If the client has a close method, call it synchronously
            if hasattr(self.client, 'close') and callable(getattr(self.client, 'close')):
                self.client.close()
                logger.info("FixedS3StorageClient - synchronous close() called")
        except Exception as e:
            # Log any errors but don't raise them during shutdown
            logger.warning(f"FixedS3StorageClient close error (non-fatal): {e}")
```

### 2. Applied Monkey Patch in Main Application (`app.py`)

Since Chainlit automatically creates S3 storage clients based on environment variables, we used a monkey patch approach to replace the problematic class before Chainlit loads it:

```python
# CRITICAL: This must be the very first thing that happens
# Apply S3 client fix before ANY other imports

from lib.custom_s3_storage import FixedS3StorageClient
import sys

def patch_s3_storage():
    """Apply the patch when the module is imported"""
    try:
        import chainlit.data.storage_clients.s3 as s3_module
        # Replace the class
        original_class = s3_module.S3StorageClient
        s3_module.S3StorageClient = FixedS3StorageClient
        print(f" Successfully patched S3StorageClient: {original_class} -> {FixedS3StorageClient}")
        return True
    except Exception as e:
        print(f" Failed to patch S3StorageClient: {e}")
        return False

# Apply the patch immediately
patch_success = patch_s3_storage()
```

### 3. Created Test Suite (`test_s3_fix.py`)

We developed a comprehensive test to verify the fix works correctly:

```python
async def test_s3_client():
    client = FixedS3StorageClient(bucket="my-bucket")
    await client.close()  # This should not crash
    print(" All tests passed!")
```

---

## Verification Results

### Before Fix
```
The user disconnected!
ERROR:    Traceback (most recent call last):
  ...
  File "chainlit/data/storage_clients/s3.py", line 91, in close
    await self.client.close()
TypeError: object NoneType can't be used in 'await' expression
ERROR:    Application shutdown failed. Exiting.
```

### After Fix
```
The user disconnected!
2025-10-08 17:18:48 - FixedS3StorageClient closing - client will be garbage collected
2025-10-08 17:18:48 - FixedS3StorageClient - synchronous close() called
PS C:\Users\jbras\Desktop\chainloot>  # Clean exit!
```

---

## Technical Details

### Why This Approach?

1. **Non-intrusive**: We don't modify the original Chainlit library files
2. **Update-safe**: When Chainlit updates, our fix remains intact
3. **Automatic**: Chainlit's auto-detection of S3 via environment variables still works
4. **Robust**: Handles edge cases and logs appropriately

### Environment Variables Used
The fix works with Chainlit's standard S3 configuration:
```bash
DATABASE_URL=postgresql://root:root@192.168.1.98:5432/chainlit
BUCKET_NAME=my-bucket
APP_AWS_ACCESS_KEY=random-key
APP_AWS_SECRET_KEY=random-key
APP_AWS_REGION=eu-central-1
DEV_AWS_ENDPOINT=http://192.168.1.98:4566  # LocalStack for local dev
```

### Files Modified/Added

#### New Files:
- `lib/custom_s3_storage.py` - Custom S3 storage client with fixed close() method
- `test_s3_fix.py` - Test suite to verify the fix

#### Modified Files:
- `app.py` - Added monkey patch at the beginning of the file

---

## Testing Performed

###  Unit Tests
- [x] Custom S3 client initialization
- [x] Custom S3 client close() method
- [x] Boto3 client attribute verification

###  Integration Tests
- [x] Full application startup
- [x] S3 storage client auto-detection
- [x] Monkey patch application
- [x] User connection and message processing
- [x] Graceful shutdown on user disconnect

###  Regression Tests
- [x] All existing functionality preserved
- [x] S3 file upload/download still works
- [x] Data persistence still works
- [x] Authentication still works

---

## Future Considerations

### Upstream Fix
This issue should be reported to the Chainlit team for a proper fix in the main library. The fix would be simple:

```python
# In chainlit/data/storage_clients/s3.py
async def close(self) -> None:
    # Instead of: await self.client.close()
    # Should be:
    if hasattr(self.client, 'close') and callable(getattr(self.client, 'close')):
        self.client.close()  # Synchronous call for boto3
```

### Monitoring
- Watch for Chainlit updates that might fix this issue upstream
- Monitor application logs for any S3-related errors
- Consider removing monkey patch when official fix is available

---

## Summary

 **Problem**: Chainlit applications with S3 storage crashed on shutdown due to incorrect async/await usage in S3StorageClient.close()

 **Solution**: Created a custom storage client with proper close() handling and applied it via monkey patching

 **Result**: Clean application shutdowns, no more crashes, preserved all existing functionality

 **Impact**: Improved user experience, cleaner logs, more reliable application lifecycle management

**Estimated Time to Resolution**: ~2 hours  
**Risk Level**: Low (non-intrusive fix)  
**Maintenance Overhead**: Minimal (watch for upstream fixes)
**10-16-2025**

- ✅ Fixed port conflict issues with TTS-WebUI
- ✅ Added Prisma CLI to Dockerfile to resolve database client generation warnings
- ✅ Enabled GPU acceleration on all containers (chainlit, ollama, tts-webui)
- ✅ Fixed voice fetching with retry logic for TTS-WebUI startup timing
- ✅ All containers healthy and app fully functional

### Complete MCP Server Catalog

- 1. Time Server (mcp-server-time)
- 2. Brave Search Server (@brave/brave-search-mcp-server)
- 3. Fetch Server (mcp-server-fetch)
- 4. Git Server (mcp-server-git)
- 5. Memory Server (@modelcontextprotocol/server-memory)
- 6. Sequential Thinking Server (@modelcontextprotocol/server-sequential-thinking)
- 7. YouTube Transcript Server (@kimtaeyoon83/mcp-server-youtube-transcript)
- 8. Wikipedia Server (wikipedia-mcp)

See the full readme for mcp docs\serverside-mcp-features.md

**10-06-2025**

Beta Release 0.1 is Live! Check the releases tag, ->
This release implements Character Profiles, you can hot swap between Yoda, C3PO, and Tony Stark. They each have their own system prompts and voice presets that will persist (I hope).

- Standard edition, Master Yoda
- C3PO
- Stark

![model_settings](https://github.com/thesavant42/chainloot/blob/main/docs/pics/selected-stark.png?raw=true)

**10-03-2025**

Latest commit: Transcription via microphone widget is complete.

![demo](https://github.com/thesavant42/chainloot/blob/main/docs/pics/demo.png?raw=true)
