
import os
import csv
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")  # <-- defina no Railway (Environment Variables)
ARQUIVO = "gastos.csv"
MSG_LIMIT = 3800  # margem para evitar 4096 chars do Telegram

# -------- utils --------
def iniciar_arquivo():
    """Garante que o CSV existe com cabeçalhos."""
    try:
        with open(ARQUIVO, "x", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["data", "valor", "descricao"])
    except FileExistsError:
        pass

def send_em_chunks_factory(send_func):
    """Retorna uma função que quebra mensagens grandes em partes."""
    async def _send(text, **kwargs):
        if len(text) <= MSG_LIMIT:
            return await send_func(text, **kwargs)
        start = 0
        while start < len(text):
            end = min(start + MSG_LIMIT, len(text))
            # evita cortar no meio de uma linha
            if end < len(text):
                nl = text.rfind("\n", start, end)
                if nl != -1 and nl > start:
                    end = nl
            await send_func(text[start:end], **kwargs)
            start = end
    return _send

# -------- handlers --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send = send_em_chunks_factory(update.message.reply_text)
    await send(
        "💬 *Controle de Gastos*\n\n"
        "Comandos:\n"
        "• /add <valor> <descrição>\n"
        "• /total — total do dia\n"
        "• /mes — lista todos os gastos do mês + total\n"
        "• /reset — apaga o histórico",
        parse_mode="Markdown"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Use: /add <valor> <descrição>")
        return
    try:
        valor = float(context.args[0].replace(",", "."))
    except ValueError:
        await update.message.reply_text("Valor inválido. Ex: /add 25 almoço")
        return

    descricao = " ".join(context.args[1:])
    data = datetime.now().strftime("%Y-%m-%d")

    with open(ARQUIVO, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([data, valor, descricao])

    await update.message.reply_text(f"✅ Gasto adicionado: R${valor:.2f} — {descricao}")

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    soma = 0.0
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for linha in reader:
                if linha["data"] == data_hoje:
                    soma += float(linha["valor"])
    except FileNotFoundError:
        await update.message.reply_text("Nenhum gasto registrado ainda.")
        return
    await update.message.reply_text(f"📅 Total de hoje: R${soma:.2f}")

async def mes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send = send_em_chunks_factory(update.message.reply_text)
    ym = datetime.now().strftime("%Y-%m")   # mês atual YYYY-MM
    soma = 0.0
    linhas = []

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for linha in reader:
                if linha["data"].startswith(ym):
                    valor = float(linha["valor"])
                    soma += valor
                    data_bonita = datetime.strptime(linha["data"], "%Y-%m-%d").strftime("%d/%m")
                    desc = linha["descricao"] or "(sem descrição)"
                    linhas.append(f"• {data_bonita} — {desc} — R${valor:.2f}")
    except FileNotFoundError:
        await update.message.reply_text("Nenhum gasto registrado ainda.")
        return

    if not linhas:
        await update.message.reply_text("📭 Nenhum gasto neste mês ainda.")
        return

    header = f"🗓️ *Gastos de {ym}*\n\n"
    footer = f"\n\n💰 *Total do mês:* R${soma:.2f}"
    texto = header + "\n".join(linhas) + footer
    await send(texto, parse_mode="Markdown")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # recria o CSV só com cabeçalhos
    with open(ARQUIVO, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["data", "valor", "descricao"])
    await update.message.reply_text("🧹 Histórico apagado!")

def main():
    if not TOKEN:
        raise RuntimeError("Defina a variável de ambiente TOKEN com o token do seu bot.")
    print("Iniciando bot de gastos...")
    iniciar_arquivo()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("mes", mes))
    app.add_handler(CommandHandler("reset", reset))

    app.run_polling()

if __name__ == "__main__":
    main()
