from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.db.models import Count
from django.utils import timezone

from blog.models import Comment, Post


def get_comment_and_check_permission(request, comment_id):
    """Получает комментарий и проверяет разрешение пользователя."""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        raise Http404('У вас нет доступа к этому комментарию.')
    return comment


def render_comment_template(request, comment, form):
    """Рендерит шаблон комментария."""
    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)


def get_post(post_id):
    """Возвращает объект Post по ID."""
    return get_object_or_404(Post, id=post_id)


def get_objects(
        objects=Post.objects,
        profile_user=None,
        need_count=True,
        sorted_string="-pub_date",
        need_filter=True):
    """Вернуть queryset"""
    if need_filter:
        if profile_user:
            objects = objects.filter(author=profile_user)
        else:
            objects = objects.filter(
                is_published=True, category__is_published=True,
                pub_date__lte=timezone.now(),)
   
    if need_count:
        objects = objects.annotate(comment_count=Count('comments'))
    if sorted_string:
        objects = objects.order_by(sorted_string)
    
    return objects
