# 🕵️‍♂️ Auditor Bot

The **Auditor** is an automated monitoring system for Discord, designed to ensure the integrity of channels through real-time audit protocols. It filters media and links, and manages message persistence.

---

## ✨ Main Features

* 🛡️ **NSFW Protocol:** Automatic blocking of attachments and links in unauthorized channels.

* 🧹 **Auto-Cleanup:** System programmed to delete messages after 24 hours.

* 📡 **Dynamic Latency:** Constant monitoring of API response.

* 🎨 **Embedded Interface:** Clean and professional communication through Discord's visual components.

---

## 🚀 Automatic Deployment (GitHub Actions)

This project is structured to be **100% self-sufficient** within the GitHub ecosystem.

1. **Fork:** Fork this repository.

2. **Secrets:** Go to `Settings` > `Secrets and variables` > `Actions` and add your `DISCORD_TOKEN`.

3. **Activation:** In the `Actions` tab, enable Workflows and run `Auditor 24/7 Hosting`.

GitHub Actions will take care of keeping the Auditor online, restarting the monitoring cycle periodically.

---

## 🛠️ Installation for Developers

To expand the Auditor's functionality locally:

```bash
git clone https://github.com
cd auditor-bot
pip install -r requirements.txt
python main.py
