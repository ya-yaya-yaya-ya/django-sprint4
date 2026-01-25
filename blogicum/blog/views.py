from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, UpdateView)

from blog.forms import CommentForm, PostForm, ProfileForm, RegisterForm
from blog.models import Category
from constants import PAGINATE_COUNT
from mixins import PostCheckMixin, PostMixin
from service import (get_comment_and_check_permission, get_objects, get_post,
                     render_comment_template)


def paginate_queryset(queryset, request, paginate_count=PAGINATE_COUNT):
    """Функция для пагинации переданного queryset."""
    paginator = Paginator(queryset, paginate_count)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@login_required
def add_comment(request, post_id):
    """Добавляет комментарий к записи."""
    post = get_post(post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирует комментарий."""
    comment = get_comment_and_check_permission(request, comment_id)

    form = CommentForm(request.POST or None, instance=comment)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    return render_comment_template(request, comment, form)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаляет комментарий."""
    comment = get_comment_and_check_permission(request, comment_id)

    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', post_id)

    template = 'blog/comment.html'
    context = {'comment': comment}
    return render(request, template, context)


class RegistrationView(FormView):
    """Отображение страницы регистрации."""

    template_name = 'registration/registration_form.html'
    form_class = RegisterForm
    success_url = reverse_lazy('blog:index')


class ProfileDetailView(DetailView):
    """Отображение страницы профиля."""

    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')

        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_name = self.kwargs.get('username')
        profile_user = get_object_or_404(User, username=user_name)
        user_posts = get_objects(profile_user=profile_user)
        context['page_obj'] = paginate_queryset(user_posts, self.request)
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Отображение страницы редактирования профиля."""

    model = User
    template_name = 'blog/user.html'
    form_class = ProfileForm
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return get_object_or_404(User, username=self.request.user.username)


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    """Отображение страницы создания поста."""

    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class PostUpdateView(LoginRequiredMixin, PostMixin,
                     PostCheckMixin, UpdateView):
    """Отображение страницы редактирования поста."""

    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs[self.pk_url_kwarg]}
        )


class PostDeleteView(PostMixin,
                     PostCheckMixin, DeleteView):
    """Страница удаления поста."""

    def get_success_url(self):
        return reverse('blog:index')


class PublishedPostsView(PostMixin, ListView):
    """Отображает главную страницу с постами."""

    template_name = 'blog/index.html'
    paginate_by = PAGINATE_COUNT

    def get_queryset(self):
        return get_objects()


class PostDetailView(LoginRequiredMixin, PostMixin, DetailView):
    """Отображает страницу поста."""

    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(self.get_queryset(), id=post_id)

        if self.request.user != post.author and not post.is_published:
            raise Http404('Пост недоступен.')
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author'))
        return context


class CategoryDetailView(DetailView):
    """Отображает страницу с постами выбранной категории."""

    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'category'

    def get_object(self, queryset=None):
        category = super().get_object(queryset)
        if not category.is_published:
            raise Http404('Категория недоступна.')
        return category

    def get_context_data(self, **kwargs):
        category_slug = self.kwargs.get('slug')
        category = get_object_or_404(
            Category.objects.all(), slug=category_slug,
            is_published=True)
        context = super().get_context_data(**kwargs)
        posts = get_objects()
        posts = posts.filter(category=category)
        paginator = Paginator(posts, PAGINATE_COUNT)
        page_obj = paginator.get_page(PAGINATE_COUNT)
        context['page_obj'] = page_obj
        return context
