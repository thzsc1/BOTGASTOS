
# Bot de Gastos no Telegram (24h no Railway)

Este projeto roda um bot de Telegram para registrar e somar gastos, com comandos:
- `/add <valor> <descrição>`
- `/total`
- `/mes`
- `/reset`

## Rodar localmente
```bash
pip install -r requirements.txt
set TOKEN=seu_token_aqui  # Windows (PowerShell: $env:TOKEN="...")
export TOKEN=seu_token_aqui # Linux/macOS
python meugasto.py
```

## Deploy 24h no Railway
1. Crie um repositório no GitHub com estes arquivos.
2. Acesse https://railway.com → New Project → Deploy from GitHub → selecione o repositório.
3. Em *Variables*/Environment, crie `TOKEN` com o token do seu bot (sem aspas).
4. Em *Start Command*, deixe `python meugasto.py`.
5. Veja os *Logs*: deve aparecer `Iniciando bot de gastos...`.
6. No Telegram, envie `/start` ao seu bot.

### Resolvendo problemas
- **Invalid token**: Gere token no @BotFather (`/token`) e atualize a variável `TOKEN`.
- **Conflict: terminated by other getUpdates**: Acesse
  `https://api.telegram.org/bot<SEU_TOKEN>/deleteWebhook` e reinicie.
- **Sem logs**: verifique se o `requirements.txt` foi instalado e se o *Start Command* está correto.

---

**Segurança**: Nunca comite o *token* no repositório. Use a variável de ambiente `TOKEN`.
