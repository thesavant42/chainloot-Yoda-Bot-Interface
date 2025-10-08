# Testing STT API Independently

To isolate if the issue is with the Chainlit integration or the STT API itself, test the Whisper transcription endpoint directly using curl. This will send the provided 'docs/stives.wav' file to http://192.168.1.98:7778/v1/audio/transcriptions and check if it returns the expected transcription.

## Expected Transcription
The WAV file contains the riddle: "As I was going to St. Ives, I met a man with seven wives. Each wife had seven sacks, each sack had seven cats, each cat had seven kits, kits, cats, sacks, and wives. How many were there going to St. Ives?"

## Curl Command (Cross-Platform, Works in Windows PowerShell/cmd, macOS, Linux)
Run this command from the workspace directory (c:\Users\jbras\Desktop\chainloot) in your terminal or PowerShell:

```
curl -X POST "http://192.168.1.98:7778/v1/audio/transcriptions" -H "Authorization: Bearer lm-studio" -F model="openai/whisper-small.en" -F file="@docs/stives.wav" -F response_format="text"
```

### Windows-Specific Notes
- Curl is built into Windows 10/11 (PowerShell or cmd). If not available, install it via Chocolatey (`choco install curl`) or use the PowerShell equivalent below.
- **PowerShell Alternative (Invoke-RestMethod)**:
  ```
  $boundary = [System.Guid]::NewGuid().ToString()
  $LF = "`r`n"
  $bodyLines = @(
      "--$boundary",
      'Content-Disposition: form-data; name="model"',
      "",
      "openai/whisper-small.en",
      "--$boundary",
      'Content-Disposition: form-data; name="file"; filename="stives.wav"',
      'Content-Type: audio/wav',
      "",
      [System.IO.File]::ReadAllBytes((Resolve-Path "docs/stives.wav"))
      "--$boundary--"
  ) -join $LF
  Invoke-RestMethod -Uri "http://192.168.1.98:7778/v1/audio/transcriptions" -Method Post -ContentType "multipart/form-data; boundary=$boundary" -Headers @{Authorization = "Bearer lm-studio"} -Body ([System.Text.Encoding]::UTF8.GetBytes($bodyLines))
  ```

### Parameters Explained
- **model**: Uses "openai/whisper-small.en" from config.json.
- **file**: The WAV file path relative to the current directory.
- **response_format**: "text" for plain transcription text.
- **Authorization**: Uses "lm-studio" as the API key, matching the config.

## Expected Output
If successful, you should see the transcription text matching the expected riddle above. If there's an error (e.g., network issue, invalid file, API down), it will show in the response.

## Next Steps
1. Run the curl command (or PowerShell alternative).
2. Copy and paste the full output (success or error) back to me.
3. If it works, the issue is likely in Chainlit's audio handling (e.g., message.elements not capturing mic audio properly).
4. If it fails, check network connectivity or the STT server status.

This test also verifies network connectivity to the endpoint.