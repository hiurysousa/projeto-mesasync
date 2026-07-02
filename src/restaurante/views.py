from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Estabelecimento, Mesa, Categoria, Produto, Pedido, ItemPedido, TransacaoHistorica, ItemTransacaoHistorico   
from decimal import Decimal
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import user_passes_test
import json

# ==========================================
# FRENTE 1: MENU DO CLIENTE (Via QR Code)
# ==========================================

def menu_cliente(request, mesa_id):
    # Puxa a mesa real do banco de dados
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    # Busca o estabelecimento e os produtos/categorias dele
    estabelecimento = mesa.estabelecimento
    categorias = Categoria.objects.filter(estabelecimento=estabelecimento)
    produtos = Produto.objects.filter(estabelecimento=estabelecimento, disponivel=True)
    
    context = {
        'mesa': mesa,
        'estabelecimento': estabelecimento,
        'categorias': categorias,
        'produtos': produtos,
    }
    
    # ATENÇÃO AQUI: Garanta que o template seja o do cardápio!
    return render(request, 'cliente/mesasync_cardapio.html', context)


# Mapeia o valor enviado pelo front-end para os choices do model TransacaoHistorica
MAPA_PAGAMENTO_TRANSACAO = {
    'pix': 'PIX',
    'dinheiro': 'DINHEIRO',
    'cartao': 'CARTAO_CREDITO',
}


def criar_pedido_ajax(request, mesa_id):
    """Recebe o carrinho via requisição AJAX (JSON), salva o pedido no banco e,
    como MVP sem gateway de pagamento, já registra a transação histórica na hora
    (o cliente escolhe a forma de pagamento e o pedido já entra como 'pago')."""
    if request.method == 'POST':
        mesa = get_object_or_404(Mesa, id=mesa_id)
        data = json.loads(request.body)

        # Aceita tanto as chaves do cardápio atual (cliente/pagamento)
        # quanto as antigas (nome_cliente/forma_pagamento), por compatibilidade.
        nome_cliente = data.get('cliente') or data.get('nome_cliente') or 'Cliente Anonimizado'
        pagamento_front = data.get('pagamento') or data.get('forma_pagamento') or 'pix'
        itens_carrinho = data.get('itens', [])  # [{'produto_id', 'quantidade', ...}]

        if not itens_carrinho:
            return JsonResponse({'success': False, 'error': 'O carrinho está vazio.'}, status=400)

        # 1. Cria a instância principal do Pedido (visão da cozinha/painel)
        pedido = Pedido.objects.create(
            mesa=mesa,
            nome_cliente=nome_cliente,
            forma_pagamento=pagamento_front,
            status=Pedido.Status.NOVO,
            total_pedido=0
        )

        total_acumulado = Decimal('0.00')
        itens_para_historico = []

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

            itens_para_historico.append({
                'produto_nome': produto.nome,
                'categoria_nome': produto.categoria.nome if produto.categoria else 'Geral',
                'quantidade': quantidade,
                'preco_unitario': produto.preco,
            })

        # 3. Atualiza o total do pedido
        pedido.total_pedido = total_acumulado
        pedido.save()

        # 4. MVP: registra direto a transação histórica, "simulando" o pagamento
        #    confirmado. É isso que alimenta o dashboard automaticamente.
        forma_pagamento_transacao = MAPA_PAGAMENTO_TRANSACAO.get(pagamento_front, 'PIX')

        transacao = TransacaoHistorica.objects.create(
            estabelecimento=mesa.estabelecimento,
            numero_mesa=mesa.numero_mesa,
            forma_pagamento=forma_pagamento_transacao,
            valor_total=total_acumulado,
        )

        for item in itens_para_historico:
            ItemTransacaoHistorico.objects.create(
                transacao=transacao,
                produto_nome=item['produto_nome'],
                categoria_nome=item['categoria_nome'],
                quantidade=item['quantidade'],
                preco_unitario=item['preco_unitario'],
            )

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

def simular_finalizar_pagamento(request, mesa_id):
    """
    View acionada quando o cliente ou garçom clica em 'Pagar' (Pix, Cartão, etc.)
    A priori, ela apenas simula o sucesso e migra os dados ativos para o histórico admin.
    """
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    # 1. Recuperar o pedido/itens ativos desta mesa (ajuste conforme suas models atuais de carrinho)
    # Exemplo genérico: supondo que sua mesa tem uma relação com pedidos pendentes
    pedidos_ativos = mesa.pedidos.filter(status='pendente') # Ajuste de acordo com suas models de pedido ativo
    
    if not pedidos_ativos.exists():
        messages.warning(request, "Esta mesa não possui itens ativos para pagamento.")
        return redirect('url_do_seu_cardapio_ou_painel')

    # Calcular o valor total dinamicamente dos itens ativos
    valor_total_calculado = 0
    itens_para_historico = []

    for pedido in pedidos_ativos:
        # Supondo uma estrutura comum de ItemPedido -> Produto
        # Ajuste os nomes de atributos com base no seu código real
        valor_total_calculado += pedido.quantidade * pedido.produto.preco
        itens_para_historico.append({
            'produto_nome': pedido.produto.nome,
            'categoria_nome': pedido.produto.categoria.nome if pedido.produto.categoria else "Geral",
            'quantidade': pedido.quantidade,
            'preco_unitario': pedido.produto.preco
        })

    # 2. Criar o cabeçalho da Transação Histórica
    # Pegamos a forma de pagamento que veio do clique no botão do front-end (via POST ou parâmetro)
    forma_pagto = request.POST.get('forma_pagamento', 'PIX') 

    transacao = TransacaoHistorica.objects.create(
        estabelecimento=mesa.estabelecimento,
        numero_mesa=mesa.numero_mesa,
        forma_pagamento=forma_pagto,
        valor_total=valor_total_calculado
    )

    # 3. Mover os itens para a tabela histórica
    for item in itens_para_historico:
        ItemTransacaoHistorico.objects.create(
            transacao=transacao,
            produto_nome=item['produto_nome'],
            categoria_nome=item['categoria_nome'],
            quantidade=item['quantidade'],
            preco_unitario=item['preco_unitario']
        )

    # 4. Limpar/Resetar a mesa física (Deletar itens do carrinho ou mudar o status para finalizado)
    pedidos_ativos.delete() # Limpa os pedidos da mesa para deixá-la livre para o próximo cliente
    
    messages.success(request, "Pagamento processado com sucesso! Mesa liberada.")
    return redirect('url_da_pagina_de_sucesso_ou_agradecimento')

# Garante que APENAS o ADMIN do sistema possa acessar esta URL
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard_view(request):
    # Ajustado de 'data_criacao' para 'data_finalizacao'
    transacoes = TransacaoHistorica.objects.all().order_by('-data_finalizacao')
    
    faturamento_total = transacoes.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    total_atendimentos = transacoes.count()
    
    # Os choices reais do model são: PIX, DINHEIRO, CARTAO_CREDITO, CARTAO_DEBITO
    # (por isso 'CARTAO' sozinho nunca batia com 'CARTAO_CREDITO')
    pagamentos_pix = transacoes.filter(forma_pagamento__iexact='PIX').count()
    pagamentos_dinheiro = transacoes.filter(forma_pagamento__iexact='DINHEIRO').count()
    pagamentos_cartao = transacoes.filter(forma_pagamento__istartswith='CARTAO').count()

    context = {
        'faturamento_total': faturamento_total,
        'total_atendimentos': total_atendimentos,
        'grafico_labels': ['Pix', 'Dinheiro', 'Cartão'],
        'grafico_dados': [pagamentos_pix, pagamentos_dinheiro, pagamentos_cartao],
        'transacoes': transacoes[:10]
    }
    
    return render(request, 'restaurante/dashboard.html', context)