#!/bin/bash
set -e

# ==============================================================================
# Entrypoint: Khởi động Wazuh Agent → Streamlit App
# ==============================================================================

WAZUH_MANAGER_HOST="${WAZUH_HOST:-wazuh.manager}"
OSSEC_CONF="/var/ossec/etc/ossec.conf"

echo "[entrypoint] Cấu hình Wazuh Agent → manager: ${WAZUH_MANAGER_HOST}"

# Ghi đè địa chỉ manager trong ossec.conf theo biến môi trường
# (hữu ích khi hostname thay đổi hoặc dùng IP thay hostname)
if [ -f "$OSSEC_CONF" ]; then
    sed -i "s|<address>.*</address>|<address>${WAZUH_MANAGER_HOST}</address>|g" "$OSSEC_CONF"
    echo "[entrypoint] ossec.conf đã được cập nhật:"
    grep "<address>" "$OSSEC_CONF" || true
fi

# Tự động thêm localfile block để giám sát /app/logs/app.log nếu chưa có
if [ -f "$OSSEC_CONF" ]; then
    if ! grep -q "app.log" "$OSSEC_CONF"; then
        echo "[entrypoint] Thêm cấu hình giám sát /app/logs/app.log vào ossec.conf..."
        python3 -c "
with open('$OSSEC_CONF', 'r') as f:
    content = f.read()
if '</ossec_config>' in content and '/app/logs/app.log' not in content:
    block = '''
  <!-- SmartPro LLM Agent: monitor JSON app logs -->
  <localfile>
    <log_format>json</log_format>
    <location>/app/logs/app.log</location>
    <label key=\"container\">smartpro-vuln-llm-agent</label>
  </localfile>
'''
    idx = content.rfind('</ossec_config>')
    if idx != -1:
        content = content[:idx] + block + content[idx:]
        with open('$OSSEC_CONF', 'w') as f:
            f.write(content)
        print('[entrypoint] Đã chèn thành công localfile block vào ossec.conf')
"
    else
        echo "[entrypoint] /app/logs/app.log đã được cấu hình trong ossec.conf."
    fi
fi

# Khởi động dịch vụ Wazuh Agent (chạy ngầm)
echo "[entrypoint] Khởi động Wazuh Agent..."
/var/ossec/bin/wazuh-control start || true

# Đợi agent kết nối (tối đa 10 giây)
for i in $(seq 1 10); do
    if /var/ossec/bin/agent_control -i 000 >/dev/null 2>&1 || \
       /var/ossec/bin/wazuh-control status 2>/dev/null | grep -q "running"; then
        echo "[entrypoint] Wazuh Agent đang chạy (${i}s)."
        break
    fi
    echo "[entrypoint] Chờ Wazuh Agent khởi động... (${i}/10)"
    sleep 1
done

# Khởi động ứng dụng Streamlit (foreground)
echo "[entrypoint] Khởi động SmartPro Vuln LLM Agent (Streamlit)..."
exec streamlit run app/main.py \
    --server.port=8501 \
    --server.address=0.0.0.0
