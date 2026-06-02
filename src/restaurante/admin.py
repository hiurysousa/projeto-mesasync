# admin.py
from django.contrib import admin
from .models import Estabelecimento, Mesa, Categoria, Produto, Pedido, ItemPedido

# Registrando as models do MesaSync no Painel Admin
admin.site.register(Estabelecimento)
admin.site.register(Mesa)
admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(Pedido)
admin.site.register(ItemPedido)