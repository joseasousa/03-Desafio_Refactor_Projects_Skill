from database import get_db


CATEGORIES = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
CATEGORIAS_VALIDAS = CATEGORIES


def get_all_products():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM produtos")
    return [_product_to_dict(row) for row in cursor.fetchall()]


def get_product_by_id(product_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    return _product_to_dict(row) if row else None


def create_product(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO produtos (nome, descricao, preco, estoque, categoria)
        VALUES (?, ?, ?, ?, ?)
        """,
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def update_product(product_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE produtos
        SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ?
        WHERE id = ?
        """,
        (nome, descricao, preco, estoque, categoria, product_id),
    )
    db.commit()
    return cursor.rowcount > 0


def delete_product(product_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
    db.commit()
    return cursor.rowcount > 0


def search_products(term, category=None, min_price=None, max_price=None):
    cursor = get_db().cursor()
    query = "SELECT * FROM produtos WHERE 1 = 1"
    params = []

    if term:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        like_term = f"%{term}%"
        params.extend([like_term, like_term])
    if category:
        query += " AND categoria = ?"
        params.append(category)
    if min_price is not None:
        query += " AND preco >= ?"
        params.append(min_price)
    if max_price is not None:
        query += " AND preco <= ?"
        params.append(max_price)

    cursor.execute(query, params)
    return [_product_to_dict(row) for row in cursor.fetchall()]


def _product_to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


get_todos_produtos = get_all_products
get_produto_por_id = get_product_by_id
criar_produto = create_product
atualizar_produto = update_product
deletar_produto = delete_product
buscar_produtos = search_products
