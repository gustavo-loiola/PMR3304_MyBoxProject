from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Box
from .forms import BoxForm
from django.core.paginator import Paginator
from .forms import BoxForm, BoxFormUpdate  # Importa o formulário BoxForm do app store
from .models import Box  # Importa o modelo Box do app store
from django.urls import reverse_lazy, reverse
import requests
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

@login_required
def dashboard(request):
    return render(request, 'store/dashboard.html')

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

@login_required
def manage_box(request, box_id=None):
    if box_id:
        box = get_object_or_404(Box, id=box_id, seller=request.user)  # Verifica se o Box pertence ao vendedor
    else:
        box = None

    if request.method == 'POST':
        form = BoxForm(request.POST, request.FILES, instance=box)
        if form.is_valid():
            box = form.save(commit=False)
            box.seller = request.user
            box.save()
            return redirect('store:store_page', seller_id=request.user.id)  # Redireciona para a página da loja
    else:
        form = BoxForm(instance=box)

    return render(request, 'store/manage_box.html', {'form': form, 'box': box})

##############################################################################

class BoxDetailView(DetailView):
    model = Box
    template_name = 'box_details.html'

    def get_object(self):
        # Use get_object_or_404 to retrieve the Post or raise a 404 if not found
        return get_object_or_404(Box, pk=self.kwargs.get('pk'))
    
    # def get_context_data(self, *args, **kwargs):
    #     cat_menu = Category.objects.all()
    #     context = super(ArticleDetailView, self).get_context_data(*args, **kwargs)
    #     current_post = get_object_or_404(Post, id=self.kwargs['pk'])
    #     liked = False
    #     if current_post.likes.filter(id=self.request.user.id).exists():
    #         liked=True
    #     context['comments'] = self.object.comments.all().order_by('-date_added')
    #     context['total_likes'] = current_post.total_likes()
    #     context["cat_menu"] = cat_menu
    #     context['liked'] = liked
    #     return context

class AddBoxView(CreateView):
    model = Box
    form_class = BoxForm
    template_name = 'store/add_box.html'
    # fields = '__all__'
    # fields = ('title', 'tag','body')

    def form_valid(self, form):
        image_file = form.cleaned_data.get('image')
        if image_file:
            # Enviar a imagem para o Imgur
            url = "https://api.imgur.com/3/image"
            headers = {"Authorization": f"Client-ID {settings.IMGUR_CLIENT_ID}"}
            files = {'image': image_file.read()}

            response = requests.post(url, headers=headers, files=files)
            data = response.json()

            if response.status_code == 200 and data['success']:
                form.instance.image_url = data['data']['link']
            
            else:
                # Log failure details
                print("Imgur upload failed:", response.status_code, data)
            
            url = "https://api.imgur.com/3/credits"
            headers = {"Authorization": "Client-ID 017429aafa9c2c9"}

            response = requests.get(url, headers=headers)
            print("Imgur API Quota Check:", response.status_code, response.json())
        
        return super().form_valid(form)
    
    # def get_context_data(self, *args, **kwargs):
    #     cat_menu = Category.objects.all()
    #     context = super(AddPostView, self).get_context_data(*args, **kwargs)
    #     context["cat_menu"] = cat_menu
    #     return context

class UpdateBoxView(UpdateView):
    model=Box
    form_class = BoxFormUpdate
    template_name= 'store/update_box.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        image_file = form.cleaned_data.get('image')
        if image_file:
            # Enviar a imagem para o Imgur
            url = "https://api.imgur.com/3/image"
            headers = {"Authorization": f"Client-ID {settings.IMGUR_CLIENT_ID}"}
            files = {'image': image_file.read()}

            response = requests.post(url, headers=headers, files=files)
            data = response.json()

            if response.status_code == 200 and data['success']:
                form.instance.image_url = data['data']['link']
            else:
                # Log failure details
                print("Imgur upload failed:", response.status_code, data)
            
            url = "https://api.imgur.com/3/credits"
            headers = {"Authorization": "Client-ID 017429aafa9c2c9"}

            response = requests.get(url, headers=headers)
            print("Imgur API Quota Check:", response.status_code, response.json())
        
        return super().form_valid(form)
    
    # def get_context_data(self, *args, **kwargs):
    #     cat_menu = Category.objects.all()
    #     context = super(UpdatePostView, self).get_context_data(*args, **kwargs)
    #     context["cat_menu"] = cat_menu
    #     return context

class DeleteBoxView(DeleteView):
    model=Box
    template_name= 'store/delete_box.html'
    success_url = reverse_lazy('home')

    # def get_context_data(self, *args, **kwargs):
    #     cat_menu = Category.objects.all()
    #     context = super(DeletePostView, self).get_context_data(*args, **kwargs)
    #     context["cat_menu"] = cat_menu
    #     return context
    

