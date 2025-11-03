# SmolLM3 Reasoning Mode Test

This is a minimal test setup to verify SmolLM3's `/think` and `/no_think` functionality works properly with Docker Model Runner.

## Purpose
- Test if `--jinja` flag enables proper template support
- Verify `/think` and `/no_think` flags work in system messages  
- Check if thinking content is properly handled (hidden/shown)
- Validate conversation history preserves thinking tags

## Usage

1. Start the test environment:
   ```bash
   docker compose up -d
   ```

2. Access the model directly at `http://localhost:8242`

3. Test reasoning modes:
   
   **Test 1 - No Thinking:**
   ```json
   {
     "model": "smollm3-test", 
     "messages": [
       {"role": "system", "content": "/no_think"},
       {"role": "user", "content": "What's 2+2?"}
     ]
   }
   ```
   
   **Test 2 - With Thinking:**
   ```json
   {
     "model": "smollm3-test",
     "messages": [
       {"role": "system", "content": "/think"}, 
       {"role": "user", "content": "What's 2+2?"}
     ]
   }
   ```

4. Expected Results:
   - `/no_think`: Direct answer with no thinking content
   - `/think`: Answer with visible thinking process in separate section

## Cleanup
```bash
docker compose down
```