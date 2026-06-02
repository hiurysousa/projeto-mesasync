from django.urls import path
from . import views

urlpatterns = [
    # --- Rotas do Cliente (Acessadas via QR Code da Mesa) ---
    path('mesa/<uuid:mesa_id>/', views.menu_cliente, name='menu_cliente'),
    path('mesa/<uuid:mesa_id>/pedido/criar/', views.criar_pedido_ajax, name='criar_pedido_ajax'),
    path('pedido/<int:pedido_id>/sucesso/', views.sucesso_pedido, name='sucesso_pedido'),

    # --- Rotas de Gerenciamento da Barraca / Cozinha ---
    path('painel/<uuid:estabelecimento_id>/', views.painel_pedidos, name='painel_pedidos'),
    path('pedido/<int:pedido_id>/atualizar-status/', views.atualizar_status_pedido, name='atualizar_status_pedido'),
]