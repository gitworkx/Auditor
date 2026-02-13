# 🕵️‍♂️ Auditor Bot

O **Auditor** é um sistema de monitoramento automatizado para Discord, projetado para garantir a integridade dos canais através de protocolos de auditoria em tempo real. Ele atua na filtragem de mídias e links, além de gerenciar a persistência de mensagens.

---

## ✨ Funcionalidades Principais

*   🛡️ **Protocolo NSFW:** Bloqueio automático de anexos e links em canais não autorizados.
*   🧹 **Auto-Cleanup:** Sistema programado para deleção de mensagens após 24 horas.
*   📡 **Latência Dinâmica:** Monitoramento constante da resposta da API.
*   🎨 **Interface via Embeds:** Comunicação limpa e profissional através de componentes visuais do Discord.

---

## 🚀 Deploy Automático (GitHub Actions)

Este projeto foi estruturado para ser **100% autossuficiente** dentro do ecossistema GitHub.

1.  **Fork:** Realize o fork deste repositório.
2.  **Secrets:** Vá em `Settings` > `Secrets and variables` > `Actions` e adicione seu `DISCORD_TOKEN`.
3.  **Ativação:** Na aba `Actions`, habilite os Workflows e execute o `Auditor 24/7 Hosting`.

O GitHub Actions cuidará de manter o Auditor online, reiniciando o ciclo de monitoramento periodicamente.

---

## 🛠️ Instalação para Desenvolvedores

Para expandir as funcionalidades do Auditor localmente:

```bash
git clone https://github.com
cd auditor-bot
pip install -r requirements.txt
python main.py
