from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Box
from users.models import Store
from .forms import BoxForm, BoxFormUpdate
from django.core.paginator import Paginator
from .forms import BoxForm, BoxFormUpdate  # Importa o formulário BoxForm do app store
from .models import Box  # Importa o modelo Box do app store
from django.urls import reverse_lazy, reverse
import requests
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Box
from .serializers import BoxSerializer
from django.db.models import Q

def store_page(request, seller_id):
    seller = get_object_or_404(User, id=seller_id)
    boxes = Box.objects.filter(seller=seller)

    # Paginação
    paginator = Paginator(boxes, 6)  # 6 produtos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'seller': seller,
        'boxes': page_obj,
    }
    return render(request, 'store/store_page.html', context)


class BoxDetailView(DetailView):
    model = Box
    template_name = 'box_details.html'

    def get_object(self):
        # Use get_object_or_404 to retrieve the Post or raise a 404 if not found
        return get_object_or_404(Box, pk=self.kwargs.get('pk'))
    

class AddBoxView(CreateView):
    model = Box
    form_class = BoxForm
    template_name = 'store/add_box.html'
    # fields = '__all__'
    # fields = ('title', 'tag','body')

    def dispatch(self, request, *args, **kwargs):
        # Redireciona buyers ou usuários não autenticados para uma página informativa
        if not request.user.is_authenticated or not request.user.profile.is_seller:
            return redirect('store:not_seller')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Associa o vendedor à Box
        form.instance.seller = self.request.user

        # Verifica se há uma imagem
        image_file = form.cleaned_data.get('image')  # Substitua 'image' pelo nome do campo no seu form

        if image_file:
            # Enviar a imagem para o Imgur
            url = "https://api.imgur.com/3/image"
            headers = {"Authorization": f"Client-ID {settings.IMGUR_CLIENT_ID}"}
            files = {'image': image_file.read()}

            response = requests.post(url, headers=headers, files=files)
            data = response.json()

            if response.status_code == 200 and data['success']:
                try:
                    if data.get('success'):
                        form.instance.image_url = data['data']['link']  # Salva o link da imagem no campo image_url
                    else:
                        print("Erro no JSON retornado:", data)
                except ValueError:
                    print("Erro ao interpretar JSON:", response.text)                
            else:
                print("Erro no upload do Imgur:", response.text)
        
        return super().form_valid(form)

def not_seller(request):
    return render(request, 'store/not_seller.html')

    
@login_required
def manage_box(request, box_id=None):
    if not request.user.profile.is_seller:
        return HttpResponseForbidden("Apenas vendedores podem gerenciar Boxes.")

    box = None
    if box_id:
        box = get_object_or_404(Box, id=box_id, seller=request.user)

    if request.method == 'POST':
        form = BoxFormUpdate(request.POST, request.FILES, instance=box)
        if form.is_valid():
            box = form.save(commit=False)
            box.seller = request.user

            # Se foi feito upload de uma nova imagem
            if form.cleaned_data['image']:
                image_file = form.cleaned_data['image']
                url = "https://api.imgur.com/3/image"
                headers = {"Authorization": f"Client-ID {settings.IMGUR_CLIENT_ID}"}
                files = {'image': image_file.read()}

                response = requests.post(url, headers=headers, files=files)
                data = response.json()

                if response.status_code == 200 and data['success']:
                    box.image_url = data['data']['link']  # Salva o link da nova imagem da Box
                else:
                    print("Erro no upload do Imgur:", response.text)

            box.save()
            return redirect('store:store_page', seller_id=request.user.id)
    else:
        form = BoxFormUpdate(instance=box)

    return render(request, 'store/manage_box.html', {'form': form, 'box': box})

    
class DeleteBoxView(DeleteView):
    model=Box
    template_name= 'store/delete_box.html'
    success_url = reverse_lazy('home:home')


def search_stores(request):
    query = request.GET.get('q')  # Recupera o termo da barra de pesquisa
    results = Store.objects.filter(store_name__icontains=query) if query else []  # Filtra as lojas com base na pesquisa
    
    # Adiciona paginação aos resultados
    paginator = Paginator(results, 16)  # Limita 16 lojas por página
    page_number = request.GET.get('page')  # Obtém o número da página da URL
    stores = paginator.get_page(page_number)  # Obtém a página de lojas correspondente

    return render(request, 'store/search_stores.html', {'results': results, 'query': query, 'stores': stores})

class BoxListAPIView(APIView):
    def get(self, request):
        # Obter parâmetros de busca
        query_param = request.GET.get('q', '').strip()  # Termo de busca
        price_filter = request.GET.get('price', 'all')  # Filtro de preço
        tag_filter = request.GET.get('tag', None)  # Filtro de categoria

        # Construir a consulta inicial
        query = Q()

        # Adicionar busca por termo (nome ou descrição)
        if query_param:
            query &= Q(name__icontains=query_param) | Q(description__icontains=query_param)

        # Filtrar por preço
        if price_filter == 'under_25':
            query &= Q(price__lt=25)
        elif price_filter == 'under_50':
            query &= Q(price__lt=50)
        elif price_filter == 'under_100':
            query &= Q(price__lt=100)
        elif price_filter == 'under_200':
            query &= Q(price__lt=200)
        elif price_filter == 'above_200':
            query &= Q(price__gte=200)

        # Filtrar por categoria (tag)
        if tag_filter:
            query &= Q(tag__iexact=tag_filter)

        # Aplicar os filtros à consulta
        boxes = Box.objects.filter(query)

        # Serializar os resultados
        serializer = BoxSerializer(boxes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

