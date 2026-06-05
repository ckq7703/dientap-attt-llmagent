#!/bin/bash
# =============================================================================
# apply-wazuh-config.sh
# Script tự động áp dụng cấu hình Wazuh để giám sát SmartPro LLM Agent
#
# Thực hiện:
#   1. Copy decoder + rules vào Wazuh Manager
#   2. Thêm localfile vào Wazuh Manager ossec.conf (nhận log từ Agent)
#   3. Thêm localfile vào Agent ossec.conf (thu thập /app/logs/app.log)
#   4. Reload Manager và restart Agent
# =============================================================================
set -e

WAZUH_MANAGER="single-node-wazuh.manager-1"
AGENT_CONTAINER="smartpro-vuln-llm-agent"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================================"
echo " SmartPro LLM Agent — Wazuh Config Deployment"
echo "============================================================"

# --------------------------------------------------------------------------
# BƯỚC 1: Copy decoder vào Manager
# --------------------------------------------------------------------------
echo ""
echo "[1/5] Copy decoder → Manager /var/ossec/etc/decoders/"
docker cp "${SCRIPT_DIR}/decoders/llm_agent_decoder.xml" \
    "${WAZUH_MANAGER}:/var/ossec/etc/decoders/llm_agent_decoder.xml"
echo "      ✅ llm_agent_decoder.xml"

# --------------------------------------------------------------------------
# BƯỚC 2: Copy rules vào Manager
# --------------------------------------------------------------------------
echo ""
echo "[2/5] Copy rules → Manager /var/ossec/etc/rules/"
docker cp "${SCRIPT_DIR}/rules/llm_agent_rules.xml" \
    "${WAZUH_MANAGER}:/var/ossec/etc/rules/llm_agent_rules.xml"
echo "      ✅ llm_agent_rules.xml"

# --------------------------------------------------------------------------
# BƯỚC 3: Thêm localfile vào Wazuh Agent (thu thập /app/logs/app.log)
# --------------------------------------------------------------------------
echo ""
echo "[3/5] Cấu hình Agent localfile → theo dõi /app/logs/app.log"

docker exec "${AGENT_CONTAINER}" bash -c '
OSSEC_CONF="/var/ossec/etc/ossec.conf"

# Kiểm tra nếu đã có localfile này rồi thì bỏ qua
if grep -q "app.log" "$OSSEC_CONF" 2>/dev/null; then
    echo "      ℹ️  /app/logs/app.log đã được cấu hình rồi, bỏ qua."
    exit 0
fi

# Thêm localfile block trước tag </ossec_config> cuối cùng
LOCALFILE_BLOCK="
  <!-- SmartPro LLM Agent: monitor JSON app logs -->
  <localfile>
    <log_format>json</log_format>
    <location>/app/logs/app.log</location>
    <label key=\"container\">smartpro-vuln-llm-agent</label>
  </localfile>
"

# Insert trước dòng </ossec_config> cuối
python3 -c "
import re, sys
with open(\"$OSSEC_CONF\", \"r\") as f:
    content = f.read()

block = \"\"\"
  <!-- SmartPro LLM Agent: monitor JSON app logs -->
  <localfile>
    <log_format>json</log_format>
    <location>/app/logs/app.log</location>
    <label key=\\\"container\\\">smartpro-vuln-llm-agent</label>
  </localfile>
\"\"\"

# Chèn vào trước </ossec_config> cuối cùng
idx = content.rfind(\"</ossec_config>\")
if idx != -1:
    content = content[:idx] + block + content[idx:]

with open(\"$OSSEC_CONF\", \"w\") as f:
    f.write(content)
print(\"      ✅ Đã thêm localfile /app/logs/app.log vào ossec.conf\")
"
'

# --------------------------------------------------------------------------
# BƯỚC 4: Reload Wazuh Manager để nạp decoder và rules mới
# --------------------------------------------------------------------------
echo ""
echo "[4/5] Reload Wazuh Manager (nạp decoder + rules mới)..."
docker exec "${WAZUH_MANAGER}" /var/ossec/bin/wazuh-control restart 2>&1 | tail -5
echo "      ✅ Manager reloaded"

# --------------------------------------------------------------------------
# BƯỚC 5: Restart Wazuh Agent để áp dụng localfile mới
# --------------------------------------------------------------------------
echo ""
echo "[5/5] Restart Wazuh Agent trong ${AGENT_CONTAINER}..."
docker exec "${AGENT_CONTAINER}" /var/ossec/bin/wazuh-control restart 2>&1 | tail -5
echo "      ✅ Agent restarted"

# --------------------------------------------------------------------------
# Kiểm tra nhanh
# --------------------------------------------------------------------------
echo ""
echo "============================================================"
echo " Kiểm tra nhanh"
echo "============================================================"

echo ""
echo "▶ Decoder đã đăng ký:"
docker exec "${WAZUH_MANAGER}" bash -c \
    'grep -l "llm-agent" /var/ossec/etc/decoders/ 2>/dev/null || echo "  (kiểm tra thủ công)"'

echo ""
echo "▶ Rules đã đăng ký:"
docker exec "${WAZUH_MANAGER}" bash -c \
    'ls /var/ossec/etc/rules/llm_agent_rules.xml 2>/dev/null && echo "  ✅ llm_agent_rules.xml tồn tại" || echo "  ❌ Không tìm thấy"'

echo ""
echo "▶ Agent đang theo dõi:"
docker exec "${AGENT_CONTAINER}" bash -c \
    'grep -A3 "app.log" /var/ossec/etc/ossec.conf 2>/dev/null || echo "  (chưa cấu hình)"'

echo ""
echo "▶ Agents đã đăng ký với Manager:"
docker exec "${WAZUH_MANAGER}" /var/ossec/bin/manage_agents -l 2>/dev/null | head -10

echo ""
echo "============================================================"
echo " HOÀN TẤT! Wazuh đang giám sát SmartPro LLM Agent."
echo ""
echo " Test bằng lệnh:"
echo "   docker exec ${AGENT_CONTAINER} cat /app/logs/app.log | tail -5"
echo ""
echo " Xem alerts trên Wazuh Dashboard:"
echo "   https://localhost:443  (admin / SecretPassword)"
echo "============================================================"
