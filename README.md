# 🛡️ SmartPro Vuln LLM Agent + Wazuh SIEM Stack

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-quochigh-blue?logo=docker)](https://hub.docker.com/u/quochigh)
[![GitHub](https://img.shields.io/badge/GitHub-dientap--attt--llmagent-black?logo=github)](https://github.com/ckq7703/dientap-attt-llmagent)
[![Wazuh](https://img.shields.io/badge/Wazuh-4.14.5-00A1E0?logo=wazuh)](https://wazuh.com)

Hệ thống tích hợp **AI Chatbot bảo mật** với **nền tảng giám sát SIEM Wazuh**, được thiết kế để phát hiện và cảnh báo tự động các cuộc tấn công AI-specific như Prompt Injection, SQL Injection, và IDOR. Toàn bộ stack được đóng gói thành các Docker image pre-built, hỗ trợ deploy một lần duy nhất qua Portainer mà **không cần build lại**.

---

## 📐 Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Network                         │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Wazuh      │    │   Wazuh      │    │   Wazuh      │  │
│  │   Indexer    │◄───│   Manager    │◄───│   Dashboard  │  │
│  │  (port 9200) │    │ (port 55000) │    │  (port 443)  │  │
│  └──────────────┘    └──────┬───────┘    └──────────────┘  │
│                             │ monitors                      │
│                      ┌──────▼───────┐                       │
│                      │   Chatbot    │                       │
│                      │ LLM Agent    │                       │
│                      │ (port 8501)  │                       │
│                      └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### Các thành phần

| Service | Image | Mô tả |
|---|---|---|
| **wazuh.indexer** | `quochigh/dientapattt-wazuh-indexer:latest` | OpenSearch lưu trữ log/alert |
| **wazuh.manager** | `quochigh/dientapattt-wazuh-manager:latest` | Engine xử lý rule, decoder, agent |
| **wazuh.dashboard** | `quochigh/dientapattt-wazuh-dashboard:latest` | Giao diện quản lý Wazuh |
| **chatbot** | `quochigh/dientapattt-smartpro-vuln-llm-agent:latest` | AI Chatbot tích hợp Wazuh logging |

> Các image trên đã tích hợp sẵn SSL certificates, custom rules, custom decoders. Không cần cấu hình thêm sau khi deploy.

---

## 🚀 Deploy nhanh qua Portainer

### Bước 1: Thêm Stack mới

Vào **Portainer → Stacks → Add stack**, chọn **Repository** và điền:

- **Repository URL**: `https://github.com/ckq7703/dientap-attt-llmagent.git`
- **Compose path**: `docker-compose.yml`

### Bước 2: Cấu hình Environment Variables

Chọn chế độ **Advanced mode** và paste nội dung sau (chỉnh sửa các giá trị cần thiết):

```env
# ── Ports (đổi nếu chạy nhiều Stack song song) ──────────────
CHATBOT_PORT=8501
DASHBOARD_PORT=443
INDEXER_PORT=9200
MANAGER_1514_PORT=1514
MANAGER_1515_PORT=1515
MANAGER_55000_PORT=55000
MANAGER_514_UDP_PORT=514

# ── LLM Model Configuration ──────────────────────────────────
model_name=openrouter/mistralai/mistral-nemo
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# ── Wazuh Credentials ────────────────────────────────────────
WAZUH_API_PASSWORD=MyS3cr37P450r.*-
WAZUH_INDEXER_PASSWORD=SecretPassword
```

### Bước 3: Deploy

Nhấn **Deploy the stack**. Toàn bộ 4 services sẽ tự động khởi chạy theo đúng thứ tự.

---

## 👥 Hỗ trợ Multi-user (nhiều Stack song song)

Mỗi người dùng có thể deploy **stack riêng biệt** trên cùng một máy chủ bằng cách đặt tên stack khác nhau và thay đổi port. Ví dụ:

| Stack | CHATBOT_PORT | DASHBOARD_PORT | INDEXER_PORT | MANAGER_55000_PORT |
|---|---|---|---|---|
| Stack User A (mặc định) | 8501 | 443 | 9200 | 55000 |
| Stack User B | 8502 | 8443 | 9201 | 55001 |
| Stack User C | 8503 | 8444 | 9202 | 55002 |

---

## 🔒 Tính năng bảo mật

### Custom Wazuh Rules & Decoders

Hệ thống tích hợp sẵn các rule phát hiện tấn công AI-specific:

| Rule ID | Loại tấn công | Mức độ |
|---|---|---|
| 100001 | Prompt Injection | High (12) |
| 100002 | SQL Injection | Critical (15) |
| 100003 | IDOR Attack | High (12) |
| 100004 | Suspicious LLM Behavior | Medium (8) |

### Log Format

Chatbot ghi log dưới dạng JSON có cấu trúc, Wazuh Manager tự động parse và phân tích:

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "WARNING",
  "attack_type": "prompt_injection",
  "user_input": "...",
  "model_response": "...",
  "session_id": "abc123"
}
```

---

## 🛠️ Cấu hình LLM Model

Hệ thống hỗ trợ nhiều nhà cung cấp LLM thông qua LiteLLM:

| Provider | Biến cần thiết | Ví dụ model_name |
|---|---|---|
| **OpenRouter** | `OPENROUTER_API_KEY` | `openrouter/mistralai/mistral-nemo` |
| **OpenAI** | `OPENAI_API_KEY` | `openai/gpt-4o` |
| **Ollama (local)** | `OLLAMA_HOST` | `ollama/mistral-nemo` |

---

## 🔄 Quy trình cập nhật

Khi thay đổi cấu hình (rule, decoder, config), cần rebuild và push images:

```bash
# 1. Chỉnh sửa file cấu hình trong wazuh-docker/single-node/config/

# 2. Rebuild images
cd wazuh-docker/single-node
docker build -f Dockerfile.indexer  -t quochigh/dientapattt-wazuh-indexer:latest  .
docker build -f Dockerfile.manager  -t quochigh/dientapattt-wazuh-manager:latest  .
docker build -f Dockerfile.dashboard -t quochigh/dientapattt-wazuh-dashboard:latest .

# 3. Push lên Docker Hub
docker push quochigh/dientapattt-wazuh-indexer:latest
docker push quochigh/dientapattt-wazuh-manager:latest
docker push quochigh/dientapattt-wazuh-dashboard:latest

# 4. Trên Portainer: Pull and redeploy stack
```

Khi thay đổi mã nguồn Chatbot:

```bash
cd /path/to/project
docker build -t quochigh/dientapattt-smartpro-vuln-llm-agent:latest ./smartpro-vuln-llm-agent/
docker push quochigh/dientapattt-smartpro-vuln-llm-agent:latest
# Trên Portainer: Pull and redeploy
```

---

## 📁 Cấu trúc thư mục

```
dientap/
├── docker-compose.yml                          # Stack chính (dùng cho Portainer)
├── .env.example                                # Mẫu biến môi trường
├── .gitignore
│
├── smartpro-vuln-llm-agent/                    # Mã nguồn AI Chatbot
│   ├── Dockerfile
│   ├── entrypoint.sh                           # Tự động cấu hình Wazuh Agent
│   ├── requirements.txt
│   ├── app/
│   └── .env.example
│
└── wazuh-docker/
    └── single-node/
        ├── Dockerfile.indexer                  # Custom image: wazuh-indexer
        ├── Dockerfile.manager                  # Custom image: wazuh-manager
        ├── Dockerfile.dashboard                # Custom image: wazuh-dashboard
        └── config/
            ├── wazuh_indexer_ssl_certs/        # SSL Certificates (tự ký)
            ├── wazuh_cluster/
            │   ├── wazuh_manager.conf          # Cấu hình Wazuh Manager
            │   ├── decoders/
            │   │   └── llm_agent_decoder.xml   # Custom JSON decoder
            │   └── rules/
            │       └── llm_agent_rules.xml     # Custom detection rules
            ├── wazuh_indexer/
            └── wazuh_dashboard/
```

---

## 📋 Yêu cầu hệ thống

| Thành phần | Tối thiểu |
|---|---|
| RAM | 6 GB |
| CPU | 4 cores |
| Disk | 20 GB |
| Docker | 20.x+ |
| Docker Compose | v2.x+ |

---

## 🔑 Thông tin đăng nhập mặc định

| Service | URL | Username | Password |
|---|---|---|---|
| Wazuh Dashboard | `https://<HOST>:443` | `admin` | `SecretPassword` |
| Wazuh API | `https://<HOST>:55000` | `wazuh-wui` | `MyS3cr37P450r.*-` |
| Chatbot | `http://<HOST>:8501` | *(không cần)* | *(không cần)* |

> ⚠️ **Lưu ý bảo mật**: Thay đổi mật khẩu mặc định trước khi triển khai lên môi trường Production.

---

## 📄 License

MIT License — Xem file [LICENSE](LICENSE) để biết thêm chi tiết.
