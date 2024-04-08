from django.shortcuts import render
from .models import *

# Create your views here.
def homepage(request):
    return render(request, 'homepage.html')


def loja(request):
    produtos = Produto.objects.all()
    context = {"produtos": produtos}
    return render(request, 'loja.html', context)


def carrinho(request):
    return render(request, 'carrinho.html')


def checkout(request):
    return render(request, 'checkout.html')



# páginas dos usuários
def minha_conta(request):
    return render(request, 'usuarios/minha_conta.html')


def login(request):
    return render(request, 'usuarios/login.html')