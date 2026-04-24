"""Compatibility shim; order persistence lives in models.order."""

from models.order import STATUS_VALIDOS
from models.order import atualizar_status_pedido
from models.order import criar_pedido
from models.order import get_pedidos_usuario
from models.order import get_todos_pedidos
