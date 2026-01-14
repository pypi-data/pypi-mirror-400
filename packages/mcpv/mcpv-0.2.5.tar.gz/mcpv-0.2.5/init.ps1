# 1. 경로 변수 설정 (사용자님의 VibeBuilder 경로)
$TARGET_DIR = "C:\Users\aa22s\Downloads\VibeBuilder"
$CONFIG_PATH = "$env:USERPROFILE\.gemini\antigravity\mcp_config.json"

# 2. JSON 파일 읽기 및 수정
if (Test-Path $CONFIG_PATH) {
    $json = Get-Content $CONFIG_PATH -Raw | ConvertFrom-Json
    
    if ($json.mcpServers.'mcpv-proxy') {
        # cwd(작업 경로)를 강제로 변경
        $json.mcpServers.'mcpv-proxy'.cwd = $TARGET_DIR
        
        # 저장
        $json | ConvertTo-Json -Depth 10 | Set-Content $CONFIG_PATH -Encoding UTF8
        Write-Host "✅ Config fixed! CWD set to: $TARGET_DIR" -ForegroundColor Green
    }
    else {
        Write-Host "❌ 'mcpv-proxy' not found in config. Please run 'mcpv install' first." -ForegroundColor Red
    }
}
else {
    Write-Host "❌ Config file not found at $CONFIG_PATH" -ForegroundColor Red
}