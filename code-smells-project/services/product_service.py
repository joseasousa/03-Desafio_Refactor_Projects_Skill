from models import CATEGORIAS_VALIDAS
from models import atualizar_produto as update_product_record
from models import criar_produto as create_product_record
from models import deletar_produto as delete_product_record
from models import get_produto_por_id


def validate_product(payload):
    if not payload:
        return None, "Dados inválidos"
    for field, message in {
        "nome": "Nome é obrigatório",
        "preco": "Preço é obrigatório",
        "estoque": "Estoque é obrigatório",
    }.items():
        if field not in payload:
            return None, message

    name = payload["nome"]
    product = {
        "nome": name,
        "descricao": payload.get("descricao", ""),
        "preco": payload["preco"],
        "estoque": payload["estoque"],
        "categoria": payload.get("categoria", "geral"),
    }

    if product["preco"] < 0:
        return None, "Preço não pode ser negativo"
    if product["estoque"] < 0:
        return None, "Estoque não pode ser negativo"
    if len(name) < 2:
        return None, "Nome muito curto"
    if len(name) > 200:
        return None, "Nome muito longo"
    if product["categoria"] not in CATEGORIAS_VALIDAS:
        return None, "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)

    return product, None


def create_product(payload):
    product, error = validate_product(payload)
    if error:
        return None, error
    product_id = create_product_record(**product)
    return {"id": product_id}, None


def update_product(product_id, payload):
    if not get_produto_por_id(product_id):
        return False, "Produto não encontrado", 404

    product, error = validate_product(payload)
    if error:
        return False, error, 400

    update_product_record(product_id, **product)
    return True, None, 200


def delete_product(product_id):
    if not get_produto_por_id(product_id):
        return False
    delete_product_record(product_id)
    return True


validar_produto = validate_product
criar_produto = create_product
atualizar_produto = update_product
deletar_produto = delete_product
