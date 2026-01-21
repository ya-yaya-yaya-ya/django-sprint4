from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect

from blog.models import Post


class PostCheckMixin:
    """Mixin для проверки прав доступа к посту."""

    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostMixin:
    """Mixin для модели Post."""

    model = Post
