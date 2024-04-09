from django.urls import path
from .views import *

urlpatterns = [
    path('', homepage, name='homepage'),
    path('loja/', loja, name='loja'),
    path('loja/<str:nome_categoria>/', loja, name='loja'),
    path('produto/<int:id_produto>/', produto, name='produto'),
    path('carrinho/', carrinho, name='carrinho'),
    path('checkout/', checkout, name='checkout'),
    path('minhaconta/', minha_conta, name='minha_conta'),
    path('login/', login, name='login'),
]