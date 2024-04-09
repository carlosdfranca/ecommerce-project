import unicodedata
from django.shortcuts import render
from .models import *

# Create your views here.
def homepage(request):
    banners = Banner.objects.all()
    context = {"banners": banners}
    return render(request, 'homepage.html', context)


def loja(request, nome_categoria=None):
    produtos = Produto.objects.all()

    if nome_categoria:
        produtos = produtos.filter(categoria__nome=nome_categoria)

    context = {"produtos": produtos}
    return render(request, 'loja.html', context)


def produto(request, id_produto):
    produto = Produto.objects.get(id=id_produto)
    itens_estoque = ItemEstoque.objects.filter(produto=produto, quantidade__gt=0)
    
    context = {"produto": produto, "itens_estoque": itens_estoque}
    
    return render(request, 'produto.html', context)


def carrinho(request):
    return render(request, 'carrinho.html')


def checkout(request):
    return render(request, 'checkout.html')



# páginas dos usuários
def minha_conta(request):
    return render(request, 'usuarios/minha_conta.html')


def login(request):
    return render(request, 'usuarios/login.html')