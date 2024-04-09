from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'telefone', 'usuario']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', ]

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ['nome', ]

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'categoria', 'tipo']

@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = ['produto', 'cor', 'tamanho', 'quantidade']

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'rua', 'numero', 'cidade', 'estado']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'codigo_transacao', 'endereco']

@admin.register(ItensPedido)
class ItensPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'itens_estoque']

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['link_destino', 'ativo']
