#!/data/data/com.termux/files/usr/bin/bash
# [PROPRIETARY & PATENT PENDING] Copyright (c) 2026 Jonathan Anthony Taylor (ViperGearLabs). All Rights Reserved.
set -euo pipefail
# camouflage: realistic UA rotation + jitter + TLS/UA coherence
UAS=(
 "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36"
 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)
ua(){ printf '%s' "${UAS[$((RANDOM % ${#UAS[@]}))]}"; }
jitter(){ sleep "$(awk -v r=$RANDOM 'BEGIN{printf "%.2f", 0.4 + (r%160)/100}')"; }
fetch(){
  local url="$1"
  jitter
  curl -fsSL --compressed \
    -H "User-Agent: $(ua)" \
    -H "Accept: application/json, text/plain, */*" \
    -H "Accept-Language: en-US,en;q=0.9" \
    --tlsv1.2 --http2 \
    -o "$2" "$url"
}
