import unicodedata
from django.shortcuts import render, redirect   
from .models import *
import uuid
from .utils import *

# Create your views here.
def homepage(request):
    banners = Banner.objects.all()
    context = {"banners": banners}
    return render(request, 'homepage.html', context)



def loja(request, filtro=None):
    # Pegando os produtos, juntamente com o Filtro (caso tenha)
    produtos = Produto.objects.all()
    produtos = filtrar_produtos(produtos, filtro)

    # Pegando o minimo e o máximo dos preços para colocar filtro da barra lateral. 
    minimo, maximo = preco_minimo_maximo(produtos)

    # Pegando as categorias existentes para colocar no filtro da barra lateral
    id_categorias = list(produtos.values_list("categoria", flat=True).distinct())
    categorias = Categoria.objects.filter(id__in=id_categorias)

    # Lógica para o filtro da barra lateral
    if request.method == "POST":
        dados = request.POST.dict()
        print(dados)
        produtos = produtos.filter(preco__gte=dados.get("preco_minimo"), preco__lte=dados.get("preco_maximo"))
        if "tamanho" in dados:
            itens = ItemEstoque.objects.filter(produto__in=produtos, tamanho=dados.get("tamanho"))
            ids_produtos = itens.values_list("produto").distinct()
            produtos = produtos.filter(id__in=ids_produtos)
        if "tipo" in dados:
            produtos = produtos.filter(tipo__slug=dados.get("tipo"))
        if "categoria" in dados:
            produtos = produtos.filter(categoria__slug=dados.get("categoria"))
    
    # Ordenando os produtos de acordo com o filtro passado na página
    ordem = request.GET.get("ordem", "")
    produtos = ordenar_por_ordem(produtos, ordem)


    # Pegando os tamanhos e ordenando-os de forma correta para o filtro da barra lateral.
    itens = ItemEstoque.objects.filter(produto__in=produtos)
    tamanhos = list(itens.values_list("tamanho", flat=True).distinct())
    tamanhos = ordrnar_tamanhos(tamanhos)

    context = {
        "produtos": produtos,
        "minimo": minimo,
        "maximo": maximo,
        "tamanhos": tamanhos,
        "categorias": categorias,
    }
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
        resposta = redirect('carrinho')
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
            else:
                id_sessao = str(uuid.uuid4())
                resposta.set_cookie(key="id_sessao", value=id_sessao, max_age=60*60*24*30)
            
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        
        # Criar o pedido , ou pegar o que está em aberto
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
        item_estoque = ItemEstoque.objects.get(produto__id=produto_id, tamanho=tamanho, cor__id=cor_id)
        item_pedido, criado = ItensPedido.objects.get_or_create(itens_estoque=item_estoque, pedido=pedido)

        # Adicionando quantidade no carrinho
        item_pedido.quantidade += 1
        item_pedido.save()

        return resposta
    else:
        return redirect('loja')
    


def remover_carrinho(request, produto_id):
    if request.method == "POST" and produto_id:
        dados = request.POST.dict()
        tamanho = dados.get("tamanho")
        cor_id = dados.get("cor")
        if not tamanho and not cor_id:
            return redirect('loja')
        
        # Pegar o cliente
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(id_sessao = id_sessao)
            else: 
                return redirect('loja')
        
        # Criar o pedido , ou pegar o que está em aberto
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
        item_estoque = ItemEstoque.objects.get(produto__id=produto_id, tamanho=tamanho, cor__id=cor_id)
        item_pedido, criado = ItensPedido.objects.get_or_create(itens_estoque=item_estoque, pedido=pedido)

        # Removendo uma unidade do carrinho
        item_pedido.quantidade -= 1
        item_pedido.save()
        if item_pedido.quantidade <= 0:
            item_pedido.delete()
        return redirect('carrinho') 
    else:
        return redirect('loja')



def carrinho(request):

    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(id_sessao = id_sessao)
        else: 
            context = {"itens_pedido": None, "pedido": None, "cliente_existente": False}
            return render(request, 'carrinho.html', context)

    pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)

    itens_pedido = ItensPedido.objects.filter(pedido=pedido)    

    context = {"itens_pedido": itens_pedido, "pedido": pedido, "cliente_existente": True}

    return render(request, 'carrinho.html', context)



def checkout(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(id_sessao = id_sessao)
        else: 
            
            return redirect('loja')

    pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)

    enderecos = Endereco.objects.filter(cliente=cliente)

    context = {"pedido": pedido, "enderecos": enderecos}

    return render(request, 'checkout.html', context)



def adicionar_endereco(request):
    if request.method == "POST":
        # Pegando o cliente
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
            else:
                return redirect('loja')

        # Pegando dados do formulário enviado
        dados = request.POST.dict()    
    
        cidade = dados.get("cidade")
        estado = dados.get("estado")
        rua = dados.get("rua")
        numero = dados.get("numero")
        complemento = dados.get("complemento")
        cep = dados.get("cep")

        # Criando o endereço no banco
        endereco = Endereco.objects.create(
            cliente=cliente,
            cidade=cidade,
            estado=estado,
            rua=rua,
            numero=int(numero),
            complemento=complemento,
            cep=cep
        )
        endereco.save()

        # Redirecionando para a página de Checkout
        return redirect("checkout")
    else:
        context = {}
        return render(request, 'adicionar_endereco.html', context)



# páginas dos usuários
def minha_conta(request):
    return render(request, 'usuarios/minha_conta.html')



def login(request):
    return render(request, 'usuarios/login.html')


# TODO quando eu criar o recurso de criar conta, ja vai ter que criar um cliente para o usuário.