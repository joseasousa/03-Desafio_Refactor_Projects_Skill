from models import STATUS_VALIDOS
from models import atualizar_status_pedido as update_order_status_record
from models import criar_pedido as create_order_record


def create_order(payload):
    if not payload:
        return None, "Dados inválidos"

    user_id = payload.get("usuario_id")
    items = payload.get("itens", [])
    if not user_id:
        return None, "Usuario ID é obrigatório"
    if not items:
        return None, "Pedido deve ter pelo menos 1 item"

    result = create_order_record(user_id, items)
    if "erro" in result:
        return None, result["erro"]
    return result, None


def update_order_status(order_id, payload):
    if not payload:
        return "Status inválido"

    new_status = payload.get("status", "")
    if new_status not in STATUS_VALIDOS:
        return "Status inválido"

    update_order_status_record(order_id, new_status)
    return None


criar_pedido = create_order
atualizar_status_pedido = update_order_status
