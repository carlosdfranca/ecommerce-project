from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Cliente(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefone = models.CharField(max_length=200, null=True, blank=True)
    id_sessao = models.CharField(max_length=200, null=True, blank=True)
    usuario = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.email)
    

class Categoria(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    slug = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.nome)
    
    class Meta:
        ordering = ['nome']


class Tipo(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    slug = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.nome)
    
    class Meta:
        ordering = ['nome']



class Cor(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    codigo_hex = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.nome)

    class Meta:
        ordering = ['nome']



class Produto(models.Model):
    imagem = models.ImageField(null=True, blank=True)
    nome = models.CharField(max_length=200, null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, null=True, blank=True, on_delete=models.SET_NULL)
    tipo = models.ForeignKey(Tipo, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return str(self.nome)
    
    def total_vendas(self):
        itens = ItensPedido.objects.filter(pedido__finalizado=True, itens_estoque__produto=self.id)
        total = sum([item.quantidade for item in itens])
        return total

        


    
class ItemEstoque(models.Model):
    produto = models.ForeignKey(Produto, null=True, blank=True, on_delete=models.SET_NULL)
    cor = models.ForeignKey(Cor, null=True, blank=True, on_delete=models.SET_NULL)
    tamanho = models.CharField(max_length=200, null=True, blank=True)
    quantidade = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.produto} - {self.cor} - {self.tamanho} - {self.quantidade}"



class Endereco(models.Model):
    rua = models.CharField(max_length=400, null=True, blank=True)
    numero = models.IntegerField(default=0)
    complemento = models.CharField(max_length=200, null=True, blank=True)
    cep = models.CharField(max_length=200, null=True, blank=True)
    cidade = models.CharField(max_length=200, null=True, blank=True)
    estado = models. CharField(max_length=200, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"{self.cliente} - {self.rua}"


class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)
    data_finalizacao = models.DateTimeField(null=True, blank=True)
    finalizado = models.BooleanField(default=False)
    codigo_transacao = models.CharField(max_length=200, null=True, blank=True)
    endereco = models.ForeignKey(Endereco, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self) -> str:
        return f"{self.id}. {self.cliente} - {self.data_finalizacao}"
    
    @property
    def quantidade_itens(self):
        itens_pedido = ItensPedido.objects.filter(pedido__id=self.id)
        quantidade_total = sum(
            [item.quantidade for item in itens_pedido]
        )
        return quantidade_total

    @property
    def preco_total_itens(self):
        itens_pedido = ItensPedido.objects.filter(pedido__id=self.id)
        preco_total = sum(
            [item.preco_total for item in itens_pedido]
        )
        return preco_total


class ItensPedido(models.Model):
    itens_estoque = models.ForeignKey(ItemEstoque, null=True, blank=True, on_delete=models.SET_NULL)
    quantidade = models.IntegerField(default=0)
    pedido = models.ForeignKey(Pedido, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f'{self.pedido} - {self.itens_estoque}'
    
    @property
    def preco_total(self):
        return self.quantidade * self.itens_estoque.produto.preco

class Banner(models.Model):
    imagem = models.ImageField(null=True, blank=True)
    link_destino = models.CharField(max_length=400, null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self) -> str:
        return str(self.link_destino)
