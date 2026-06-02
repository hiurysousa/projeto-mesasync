from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Estabelecimento, Mesa, Categoria, Produto, Pedido, ItemPedido
from decimal import Decimal
import json

# ==========================================
# FRENTE 1: MENU DO CLIENTE (Via QR Code)
# ==========================================

def menu_cliente(request, mesa_id):
    """Exibe o cardápio digital da barraca associado à mesa do QR Code."""
    # Busca a mesa ou retorna erro 404 se o ID não existir
    mesa = get_object_or_404(Mesa, id=mesa_id)
    estabelecimento = mesa.estabelecimento
    
    # Busca os dados do banco para injetar no seu HTML
    categorias = Categoria.objects.filter(estabelecimento=estabelecimento)
    produtos = Produto.objects.filter(estabelecimento=estabelecimento, disponivel=True)
    
    context = {
        'mesa': mesa,
        'estabelecimento': estabelecimento,
        'categorias': categorias,
        'produtos': produtos
    }
    
    # RENDERIZA O SEU ARQUIVO HTML ESPECÍFICO!
    return render(request, 'cliente/mesasync_cardapio.html', context)


def criar_pedido_ajax(request, mesa_id):
    """Recebe o carrinho via requisição AJAX (JSON) e salva o pedido no banco."""
    if request.method == 'POST':
        mesa = get_object_or_404(Mesa, id=mesa_id)
        data = json.loads(request.body)
        
        nome_cliente = data.get('nome_cliente', 'Cliente Anonimizado')
        forma_pagamento = data.get('forma_pagamento')
        itens_carrinho = data.get('itens', []) # Lista de dicionários [{'produto_id': ..., 'quantidade': ...}]
        
        if not itens_carrinho:
            return JsonResponse({'success': False, 'error': 'O carrinho está vazio.'}, status=400)
            
        # 1. Cria a instância principal do Pedido
        pedido = Pedido.objects.create(
            mesa=mesa,
            nome_cliente=nome_cliente,
            forma_pagamento=forma_pagamento,
            status=Pedido.Status.NOVO,
            total_pedido=0
        )
        
        total_acumulado = Decimal('0.00')
        
        # 2. Cria os itens do pedido salvando o histórico de preços
        for item in itens_carrinho:
            produto = get_object_or_404(Produto, id=item['produto_id'])
            quantidade = int(item['quantidade'])
            
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco_unitario_historico=produto.preco
            )
            total_acumulado += produto.preco * quantidade
            
        # 3. Atualiza o total do pedido
        pedido.total_pedido = total_acumulado
        pedido.save()
        
        return JsonResponse({'success': True, 'pedido_id': pedido.id})
        
    return JsonResponse({'success': False, 'error': 'Método inválido.'}, status=405)


def sucesso_pedido(request, pedido_id):
    """Tela simples de confirmação pós-pedido (substitui o antigo rastreio)."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'cliente/sucesso.html', {'pedido': pedido})


# ==========================================
# FRENTE 2: PAINEL ADMINISTRATIVO DO GERENTE / COZINHA
# ==========================================

def painel_pedidos(request, estabelecimento_id):
    """Painel de controle para a cozinha acompanhar os pedidos em tempo real."""
    estabelecimento = get_object_or_404(Estabelecimento, id=estabelecimento_id)
    
    # Busca todos os pedidos das mesas pertencentes a este estabelecimento
    pedidos = Pedido.objects.filter(mesa__estabelecimento=estabelecimento).order_by('-criado_em')
    
    context = {
        'estabelecimento': estabelecimento,
        'pedidos': pedidos
    }
    return render(request, 'gerencia/painel_pedidos.html', context)


def atualizar_status_pedido(request, pedido_id):
    """Muda o status do pedido (Novo -> Em Preparo -> Entregue) via requisição rápida."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    novo_status = request.POST.get('status')
    
    if novo_status in Pedido.Status.values:
        pedido.status = novo_status
        pedido.save()
        
    return redirect('painel_pedidos', estabelecimento_id=pedido.mesa.estabelecimento.id)