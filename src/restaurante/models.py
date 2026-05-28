import uuid
from django.db import models


class Estabelecimento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=18, unique=True)
    telefone_whatsapp = models.CharField(max_length=20)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Mesa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_mesa = models.PositiveIntegerField()
    estabelecimento = models.ForeignKey(
        Estabelecimento, on_delete=models.CASCADE, related_name='mesas'
    )

    def __str__(self):
        return f'Mesa {self.numero_mesa} — {self.estabelecimento.nome}'


class Categoria(models.Model):
    """Permite que cada barraca crie suas próprias categorias (Ex: Petiscos, Bebidas, Drinks)"""
    estabelecimento = models.ForeignKey(
        Estabelecimento, on_delete=models.CASCADE, related_name='categorias'
    )
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.nome} ({self.estabelecimento.nome})'


class Produto(models.Model):
    estabelecimento = models.ForeignKey(
        Estabelecimento, on_delete=models.CASCADE, related_name='produtos'
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, related_name='produtos'
    )
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    disponivel = models.BooleanField(default=True) # Para o dono pausar o camarão se acabar o estoque no dia

    def __str__(self):
        return f'{self.nome} — {self.estabelecimento.nome}'


class Pedido(models.Model):
    class Status(models.TextChoices):
        NOVO = 'novo', 'Novo'
        EM_PREPARO = 'em_preparo', 'Em preparo'
        ENTREGUE = 'entregue', 'Entregue'
        CANCELADO = 'cancelado', 'Cancelado'

    class FormaPagamento(models.TextChoices):
        PIX = 'pix', 'Pix'
        DINHEIRO = 'dinheiro', 'Dinheiro'
        CARTAO = 'cartao', 'Cartão'

    mesa = models.ForeignKey(
        Mesa, on_delete=models.PROTECT, related_name='pedidos'
    )
    nome_cliente = models.CharField(max_length=150) # Apenas o nome, sem atrito de login/telefone!
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NOVO
    )
    forma_pagamento = models.CharField(max_length=20, choices=FormaPagamento.choices)
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido #{self.id} — Mesa {self.mesa.numero_mesa} ({self.nome_cliente})'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='itens'
    )
    produto = models.ForeignKey(
        Produto, on_delete=models.PROTECT, related_name='itens_pedido'
    )
    quantidade = models.PositiveIntegerField()
    preco_unitario_historico = models.DecimalField(max_digits=8, decimal_places=2) # Mantém o preço do dia que comprou

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome}'