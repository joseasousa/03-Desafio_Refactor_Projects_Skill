from database import get_db


DESCONTO_ALTO_FATURAMENTO = 10000
DESCONTO_MEDIO_FATURAMENTO = 5000
DESCONTO_BAIXO_FATURAMENTO = 1000


def relatorio_vendas():
    cursor = get_db().cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0] or 0

    cursor.execute("SELECT status, COUNT(*) AS total FROM pedidos GROUP BY status")
    totais_por_status = {row["status"]: row["total"] for row in cursor.fetchall()}

    desconto = calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": totais_por_status.get("pendente", 0),
        "pedidos_aprovados": totais_por_status.get("aprovado", 0),
        "pedidos_cancelados": totais_por_status.get("cancelado", 0),
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }


def calcular_desconto(faturamento):
    if faturamento > DESCONTO_ALTO_FATURAMENTO:
        return faturamento * 0.1
    if faturamento > DESCONTO_MEDIO_FATURAMENTO:
        return faturamento * 0.05
    if faturamento > DESCONTO_BAIXO_FATURAMENTO:
        return faturamento * 0.02
    return 0
