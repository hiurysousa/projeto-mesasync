# admin.py
from django.contrib import admin
from .models import Estabelecimento, Mesa, Categoria, Produto, Pedido, ItemPedido, TransacaoHistorica, ItemTransacaoHistorico
from django.db.models import Sum, Count

# Registrando as models do MesaSync no Painel Admin
admin.site.register(Estabelecimento)
admin.site.register(Mesa)
admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(Pedido)
admin.site.register(ItemPedido)

class ItemTransacaoInline(admin.TabularInline):
    model = ItemTransacaoHistorico
    extra = 0
    readonly_fields = ['produto_nome', 'categoria_nome', 'quantidade', 'preco_unitario']


# Deixe a classe exatamente como você enviou:
@admin.register(TransacaoHistorica)
class TransacaoHistoricaAdmin(admin.ModelAdmin):
    list_display = ['id', 'numero_mesa', 'data_finalizacao', 'forma_pagamento', 'valor_total']
    list_filter = ['forma_pagamento', 'data_finalizacao', 'numero_mesa']
    readonly_fields = ['estabelecimento', 'numero_mesa', 'data_finalizacao', 'forma_pagamento', 'valor_total']
    inlines = [ItemTransacaoInline] # Certifique-se que o ItemTransacaoInline está definido acima neste arquivo

    # Um mini "dashboard" estatístico fake/estático direto no topo do admin
    def changelist_view(self, request, extra_context=None):
        # Cálculos de agregação em tempo real para a banca ver operando
        total_faturado = TransacaoHistorica.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        total_vendas = TransacaoHistorica.objects.count()
        
        # Injetando os dados analíticos no contexto da página do Admin
        extra_context = extra_context or {}
        extra_context['total_faturado'] = total_faturado
        extra_context['total_vendas'] = total_vendas
        return super().changelist_view(request, extra_context=extra_context)