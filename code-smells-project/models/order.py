from database import get_db


VALID_STATUSES = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
STATUS_VALIDOS = VALID_STATUSES


def create_order(usuario_id, itens):
    db = get_db()
    cursor = db.cursor()

    try:
        products = _products_by_id(cursor, [item["produto_id"] for item in itens])
        total = 0

        for item in itens:
            product = products.get(item["produto_id"])
            if product is None:
                return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
            if product["estoque"] < item["quantidade"]:
                return {"erro": "Estoque insuficiente para " + product["nome"]}
            total += product["preco"] * item["quantidade"]

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, "pendente", total),
        )
        order_id = cursor.lastrowid

        for item in itens:
            product = products[item["produto_id"]]
            cursor.execute(
                """
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
                """,
                (order_id, item["produto_id"], item["quantidade"], product["preco"]),
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        db.commit()
        return {"pedido_id": order_id, "total": total}
    except Exception:
        db.rollback()
        raise


def get_user_orders(usuario_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
    return _orders_with_items(cursor, cursor.fetchall())


def get_all_orders():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM pedidos")
    return _orders_with_items(cursor, cursor.fetchall())


def update_order_status(order_id, new_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (new_status, order_id))
    db.commit()
    return cursor.rowcount > 0


def _products_by_id(cursor, ids):
    if not ids:
        return {}
    placeholders = ",".join("?" for _ in ids)
    cursor.execute(f"SELECT * FROM produtos WHERE id IN ({placeholders})", ids)
    return {row["id"]: row for row in cursor.fetchall()}


def _orders_with_items(cursor, rows):
    orders = [_order_to_dict(row) for row in rows]
    if not orders:
        return []

    order_ids = [order["id"] for order in orders]
    placeholders = ",".join("?" for _ in order_ids)
    cursor.execute(
        f"""
        SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome AS produto_nome
        FROM itens_pedido ip
        LEFT JOIN produtos p ON p.id = ip.produto_id
        WHERE ip.pedido_id IN ({placeholders})
        ORDER BY ip.id
        """,
        order_ids,
    )

    orders_by_id = {order["id"]: order for order in orders}
    for item in cursor.fetchall():
        orders_by_id[item["pedido_id"]]["itens"].append({
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"] or "Desconhecido",
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })
    return orders


def _order_to_dict(row):
    return {
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "status": row["status"],
        "total": row["total"],
        "criado_em": row["criado_em"],
        "itens": [],
    }


criar_pedido = create_order
get_pedidos_usuario = get_user_orders
get_todos_pedidos = get_all_orders
atualizar_status_pedido = update_order_status
