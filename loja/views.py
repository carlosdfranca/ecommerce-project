import unicodedata
from django.shortcuts import render, redirect   
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


def produto(request, id_produto, id_cor=None):
    produto = Produto.objects.get(id=id_produto)
    itens_estoque = ItemEstoque.objects.filter(produto=produto, quantidade__gt=0)

    tem_estoque = False
    cores = {}
    tamanhos = {}
    cor_selecionada = None

    if len(itens_estoque)>0:
        tem_estoque = True
        cores = {item.cor for item in itens_estoque}
        if id_cor:
            itens_estoque = ItemEstoque.objects.filter(produto=produto, quantidade__gt=0, cor__id=id_cor)
            tamanhos = {item.tamanho for item in itens_estoque}
            cor_selecionada = Cor.objects.get(id=id_cor)
    
    context = {
        "produto": produto, 
        "itens_estoque": itens_estoque, 
        "tem_estoque": tem_estoque,
        "cores": cores,
        "tamanhos": tamanhos, 
        "cor_selecionada": cor_selecionada
    }
    
    return render(request, 'produto.html', context)


def adicionar_carrinho(request, produto_id):
    if request.method == "POST" and produto_id:
        dados = request.POST.dict()
        tamanho = dados.get("tamanho")
        cor_id = dados.get("cor")
        if not tamanho and not cor_id:
            return redirect('loja')
        
        # Peagr o cliente
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            return redirect('loja')
        
        # Criar o pedido , ou pegar o que está em aberto
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
        item_estoque = ItemEstoque.objects.get(produto__id=produto_id, tamanho=tamanho, cor__id=cor_id)
        item_pedido, criado = ItensPedido.objects.get_or_create(itens_estoque=item_estoque, pedido=pedido)

        # Adicionando quantidade no carrinho
        item_pedido.quantidade += 1
        item_pedido.save()

        return redirect('carrinho') 
    else:
        return redirect('loja')
    

def remover_carrinho(request, produto_id):
    if request.method == "POST" and produto_id:
        dados = request.POST.dict()
        tamanho = dados.get("tamanho")
        cor_id = dados.get("cor")
        if not tamanho and not cor_id:
            return redirect('loja')
        
        # Peagr o cliente
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            return redirect('loja')
        
        # Criar o pedido , ou pegar o que está em aberto
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
        item_estoque = ItemEstoque.objects.get(produto__id=produto_id, tamanho=tamanho, cor__id=cor_id)
        item_pedido, criado = ItensPedido.objects.get_or_create(itens_estoque=item_estoque, pedido=pedido)

        # Removendo uma unidade do carrinho
        if item_pedido.quantidade > 1:
            item_pedido.quantidade -= 1
            item_pedido.save()
        else:
            item_pedido.delete()

        return redirect('carrinho') 
    else:
        return redirect('loja')


def carrinho(request):

    if request.user.is_authenticated:
        cliente = request.user.cliente

    pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)

    itens_pedido = ItensPedido.objects.filter(pedido=pedido)

    print(pedido)
    for item in itens_pedido:
        print(item.itens_estoque.produto.nome)

    context = {"itens_pedido": itens_pedido, "pedido": pedido}
    return render(request, 'carrinho.html', context)




def checkout(request):
    return render(request, 'checkout.html')



# páginas dos usuários
def minha_conta(request):
    return render(request, 'usuarios/minha_conta.html')


def login(request):
    return render(request, 'usuarios/login.html')


# TODO quando eu criar o recurso de criar conta, ja vai ter que criar um cliente para o usuário.