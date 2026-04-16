from database import get_db


STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def criar_pedido(usuario_id, itens):
    db = get_db()
    cursor = db.cursor()

    try:
        produtos = _produtos_por_id(cursor, [item["produto_id"] for item in itens])
        total = 0

        for item in itens:
            produto = produtos.get(item["produto_id"])
            if produto is None:
                return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": "Estoque insuficiente para " + produto["nome"]}
            total += produto["preco"] * item["quantidade"]

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, "pendente", total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            produto = produtos[item["produto_id"]]
            cursor.execute(
                """
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
                """,
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        db.commit()
        return {"pedido_id": pedido_id, "total": total}
    except Exception:
        db.rollback()
        raise


def get_pedidos_usuario(usuario_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
    return _pedidos_com_itens(cursor, cursor.fetchall())


def get_todos_pedidos():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM pedidos")
    return _pedidos_com_itens(cursor, cursor.fetchall())


def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
    return cursor.rowcount > 0


def _produtos_por_id(cursor, ids):
    if not ids:
        return {}
    placeholders = ",".join("?" for _ in ids)
    cursor.execute(f"SELECT * FROM produtos WHERE id IN ({placeholders})", ids)
    return {row["id"]: row for row in cursor.fetchall()}


def _pedidos_com_itens(cursor, rows):
    pedidos = [_pedido_to_dict(row) for row in rows]
    if not pedidos:
        return []

    pedido_ids = [pedido["id"] for pedido in pedidos]
    placeholders = ",".join("?" for _ in pedido_ids)
    cursor.execute(
        f"""
        SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome AS produto_nome
        FROM itens_pedido ip
        LEFT JOIN produtos p ON p.id = ip.produto_id
        WHERE ip.pedido_id IN ({placeholders})
        ORDER BY ip.id
        """,
        pedido_ids,
    )

    pedidos_por_id = {pedido["id"]: pedido for pedido in pedidos}
    for item in cursor.fetchall():
        pedidos_por_id[item["pedido_id"]]["itens"].append({
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"] or "Desconhecido",
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })
    return pedidos


def _pedido_to_dict(row):
    return {
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "status": row["status"],
        "total": row["total"],
        "criado_em": row["criado_em"],
        "itens": [],
    }
