# FAQ.md

## Known Issues & Troubleshooting

### Port Conflicts on Restart
**Issue**: When restarting containers, you may encounter "port already in use" errors.

**Cause**: Old containers weren't properly stopped before starting new ones.

**Solution**:
```bash
# Stop and remove old containers
docker-compose -f install/docker/docker-compose.yml down

# Or stop specific problematic containers
docker stop <container_name>
docker rm <container_name>

# Then restart
docker-compose -f install/docker/docker-compose.yml up -d
```

### Prisma CLI Not Found
**Issue**: Container logs show "Prisma could not find a package.json file" and auto-install warnings.

**Cause**: Prisma CLI not installed globally in the container.

**Solution**: Dockerfile has been updated to include `npm install -g prisma`. Rebuild the container:
```bash
docker-compose -f install/docker/docker-compose.yml build chainlit
```

### GPU Not Available in Containers
**Issue**: PyTorch/TTS operations running on CPU instead of GPU.

**Cause**: GPU configuration missing from docker-compose.yml.

**Solution**: Ensure all GPU-enabled services have this configuration:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

**Status**: ✅ Fixed - chainlit, ollama, and tts-webui all have GPU enabled.

### App Loads But API Backend Unresponsive
**Issue**: Frontend accessible but chat/API calls fail with voice selection errors.

**Cause**: TTS-WebUI not ready when app starts, causing voice fetching to fail and voice list to be empty.

**Solution**: Added retry logic to voice fetching with 5 attempts and 2-second delays. Also ensured TTS-WebUI dependency in docker-compose.yml.

**Status**: ✅ Fixed - App now waits for TTS-WebUI and retries voice fetching until successful.

### TTS-WebUI Port Conflicts
**Issue**: TTS-WebUI fails to start with "port already in use" on ports 3000, 7770, 7778.

**Cause**: Docker Desktop or other services occupying these ports.

**Solution**: 
1. Check what's using the ports: `netstat -ano | findstr "3000\|7770\|7778"`
2. Stop conflicting services or change TTS-WebUI ports in docker-compose.yml
3. Ensure old TTS-WebUI containers are stopped

### Database Connection Issues
**Issue**: Prisma migrations fail or app can't connect to PostgreSQL.

**Cause**: Database not ready when app starts.

**Solution**: The docker-compose.yml includes proper dependency management. If issues persist:
```bash
# Reset database
docker-compose -f install/docker/docker-compose.yml down -v
docker-compose -f install/docker/docker-compose.yml up -d postgres
# Wait for postgres to be ready, then start other services
```

### Build Performance Issues
**Issue**: Docker builds are slow, especially on first run.

**Solution**: 
- Enable BuildKit: `$env:DOCKER_BUILDKIT=1` (PowerShell)
- Use build cache: Subsequent builds are much faster
- Clean rebuild only when dependencies change: `docker builder prune -f`
