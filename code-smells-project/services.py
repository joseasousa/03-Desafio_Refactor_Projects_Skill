import models


def validar_produto(dados):
    if not dados:
        return None, "Dados inválidos"
    for campo, mensagem in {
        "nome": "Nome é obrigatório",
        "preco": "Preço é obrigatório",
        "estoque": "Estoque é obrigatório",
    }.items():
        if campo not in dados:
            return None, mensagem

    nome = dados["nome"]
    produto = {
        "nome": nome,
        "descricao": dados.get("descricao", ""),
        "preco": dados["preco"],
        "estoque": dados["estoque"],
        "categoria": dados.get("categoria", "geral"),
    }

    if produto["preco"] < 0:
        return None, "Preço não pode ser negativo"
    if produto["estoque"] < 0:
        return None, "Estoque não pode ser negativo"
    if len(nome) < 2:
        return None, "Nome muito curto"
    if len(nome) > 200:
        return None, "Nome muito longo"
    if produto["categoria"] not in models.CATEGORIAS_VALIDAS:
        return None, "Categoria inválida. Válidas: " + str(models.CATEGORIAS_VALIDAS)

    return produto, None


def criar_produto(dados):
    produto, erro = validar_produto(dados)
    if erro:
        return None, erro
    produto_id = models.criar_produto(**produto)
    return {"id": produto_id}, None


def atualizar_produto(produto_id, dados):
    if not models.get_produto_por_id(produto_id):
        return False, "Produto não encontrado", 404

    produto, erro = validar_produto(dados)
    if erro:
        return False, erro, 400

    models.atualizar_produto(produto_id, **produto)
    return True, None, 200


def deletar_produto(produto_id):
    if not models.get_produto_por_id(produto_id):
        return False
    models.deletar_produto(produto_id)
    return True


def criar_usuario(dados):
    if not dados:
        return None, "Dados inválidos"

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        return None, "Nome, email e senha são obrigatórios"

    return {"id": models.criar_usuario(nome, email, senha)}, None


def login(dados):
    if not dados:
        return None, "Email e senha são obrigatórios"

    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        return None, "Email e senha são obrigatórios"

    usuario = models.login_usuario(email, senha)
    if not usuario:
        return None, "Email ou senha inválidos"
    return usuario, None


def criar_pedido(dados):
    if not dados:
        return None, "Dados inválidos"

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        return None, "Usuario ID é obrigatório"
    if not itens:
        return None, "Pedido deve ter pelo menos 1 item"

    resultado = models.criar_pedido(usuario_id, itens)
    if "erro" in resultado:
        return None, resultado["erro"]
    return resultado, None


def atualizar_status_pedido(pedido_id, dados):
    if not dados:
        return "Status inválido"

    novo_status = dados.get("status", "")
    if novo_status not in models.STATUS_VALIDOS:
        return "Status inválido"

    models.atualizar_status_pedido(pedido_id, novo_status)
    return None
