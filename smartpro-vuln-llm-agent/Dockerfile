FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app

# ==============================================================================
# 1. Cài đặt gói hệ thống (bao gồm curl, gnupg2 để cài Wazuh Agent)
# ==============================================================================
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    gnupg2 \
    apt-transport-https \
    lsb-release \
    procps \
    && rm -rf /var/lib/apt/lists/*

# ==============================================================================
# 2. Cài đặt Wazuh Agent 4.x vào bên trong container
#    - GPG key → /etc/apt/trusted.gpg.d/wazuh.gpg
#    - Repo    → /etc/apt/sources.list.d/wazuh.list
#    - WAZUH_MANAGER trỏ tới hostname wazuh.manager (resolve qua Docker network
#      single-node_default lúc runtime — không cần IP cứng)
# ==============================================================================
RUN curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH \
        | gpg --no-default-keyring \
              --keyring gnupg-ring:/etc/apt/trusted.gpg.d/wazuh.gpg \
              --import \
    && chmod 644 /etc/apt/trusted.gpg.d/wazuh.gpg \
    && echo "deb https://packages.wazuh.com/4.x/apt/ stable main" \
        | tee /etc/apt/sources.list.d/wazuh.list \
    && apt-get update \
    && WAZUH_MANAGER='wazuh.manager' apt-get install -y wazuh-agent \
    && rm -rf /var/lib/apt/lists/*

# ==============================================================================
# 3. Cài đặt Python dependencies
# ==============================================================================
RUN pip install --no-cache-dir python-dotenv

COPY . /app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY config/config.toml /root/.streamlit/config.toml

# ==============================================================================
# 4. Tạo thư mục logs và data bên trong container (không mount ra ngoài host)
# ==============================================================================
RUN mkdir -p /app/logs /app/data && chmod 777 /app/logs /app/data

# Biến môi trường mặc định — có thể override qua docker-compose env_file
ENV DB_PATH=/app/data/transactions.db
ENV LLM_LOG_DIR=/app/logs
ENV WAZUH_HOST=wazuh.manager

# ==============================================================================
# 5. Entrypoint: khởi Wazuh Agent → rồi chạy Streamlit
# ==============================================================================
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["/entrypoint.sh"]