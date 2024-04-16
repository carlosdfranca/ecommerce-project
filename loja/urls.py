from django.urls import path
from .views import *

urlpatterns = [
    path('', homepage, name='homepage'),
    path('loja/', loja, name='loja'),
    path('loja/<str:nome_categoria>/', loja, name='loja'),
    path('produto/<int:id_produto>/', produto, name='produto'),
    path('produto/<int:id_produto>/<int:id_cor>', produto, name='produto'),
    path('carrinho/', carrinho, name='carrinho'),
    path('checkout/', checkout, name='checkout'),
    path('minhaconta/', minha_conta, name='minha_conta'),
    path('login/', login, name='login'),
    path('adicionarcarrinho/<int:produto_id>', adicionar_carrinho, name='adicionar_carrinho'),
    path('removercarrinho/<int:produto_id>', remover_carrinho, name='remover_carrinho'),
    path('adicionarendereco/', adicionar_endereco, name='adicionar_endereco'),
]