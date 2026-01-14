Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "mcpv" -Force -ErrorAction SilentlyContinue

# 1. 패키지 재설치 (라이브러리 업데이트)
uv pip install . --system --reinstall

# 2. [중요] 설정 파일 갱신 (MCPV_ROOT 환경변수 등록)
# 이 단계가 없으면 수정된 vault.py가 mcp_config.json에 반영되지 않습니다.
python -m mcpv install --force