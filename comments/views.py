from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import CommentForm
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from blog.models import Article
from accounts.models import BlogUser
from comments.models import Comment
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
# Create your views here.
class CommentPostView(FormView):
    form_class=CommentForm
    template_name='blog/article_detail.html'

    @method_decorator
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self,request,*args,**kwargs):
        article_id=self.kwargs['article_id']
        article=get_object_or_404(Article,pk=article_id)
        url=article.get_absolute_url()        
        return HttpResponseRedirect(url+'#comment')
        
    def form_invalid(self,form):
        '''表单校验失败执行'''
        article_id=self.kwargs['article_id']
        article=get_object_or_404(Article,pk=article_id)
        
        return self.render_to_response({'form':form,'article':article})
    
    def form_valid(self,form):
        '''表单校验'''
        user=self.request.user # 获取当前登录yonghu
        author=BlogUser.objects.get(pk=user.pk) # 获取author
        article_id=self.kwargs['article_id'] # 从url参数中获取article_id
        article=get_object_or_404(Article,pk=article_id) # 获得article_id对应的article数据

        if article.comment_status == 'c' or article.status == 'c': 
            raise ValidationError('该评论文章已关闭')
        comment=form.save(False)
        comment.article=article
        from djangoblog.utils import get_blog_setting
        settings=get_blog_setting()
        if not settings.comment_need_review:
            comment.is_enable=True
        comment.author = author # 将评论的作者设置为当前作者

        if form.cleaned_data['parent_comment_id']: # 检查是否有父级评论id
            parent_comment=Comment.objects.get(pk=form.cleaned_data['parent_comment_id'])
            comment.parent_comment=parent_comment

        comment.save(True)
        return HttpResponseRedirect('%s#div-comment-%d'%(article.get_absolute_url(),comment.pk))


