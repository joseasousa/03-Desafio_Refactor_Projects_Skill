from database import get_db


HIGH_REVENUE_DISCOUNT = 10000
MEDIUM_REVENUE_DISCOUNT = 5000
LOW_REVENUE_DISCOUNT = 1000


def sales_report():
    cursor = get_db().cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    order_count = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM pedidos")
    gross_revenue = cursor.fetchone()[0] or 0

    cursor.execute("SELECT status, COUNT(*) AS total FROM pedidos GROUP BY status")
    totals_by_status = {row["status"]: row["total"] for row in cursor.fetchall()}

    discount = calculate_discount(gross_revenue)

    return {
        "total_pedidos": order_count,
        "faturamento_bruto": round(gross_revenue, 2),
        "desconto_aplicavel": round(discount, 2),
        "faturamento_liquido": round(gross_revenue - discount, 2),
        "pedidos_pendentes": totals_by_status.get("pendente", 0),
        "pedidos_aprovados": totals_by_status.get("aprovado", 0),
        "pedidos_cancelados": totals_by_status.get("cancelado", 0),
        "ticket_medio": round(gross_revenue / order_count, 2) if order_count > 0 else 0,
    }


def calculate_discount(revenue):
    if revenue > HIGH_REVENUE_DISCOUNT:
        return revenue * 0.1
    if revenue > MEDIUM_REVENUE_DISCOUNT:
        return revenue * 0.05
    if revenue > LOW_REVENUE_DISCOUNT:
        return revenue * 0.02
    return 0


relatorio_vendas = sales_report
calcular_desconto = calculate_discount
