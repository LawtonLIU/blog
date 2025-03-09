from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.conf import settings
from blog.models import LinkShowType,Article,Category,Tag,Links
from djangoblog.utils import cache,get_blog_setting
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from comments.forms import CommentForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse

# Create your views here.
class ArticleListView(ListView):
    template_name='blog/article_index.html'
    context_object_name='article_list' # 模板名字
    page_type=''
    paginate_by=settings.PAGINATE_BY
    page_kwarg='page'
    link_type=LinkShowType.L
    
    def get_view_cache_key(self): #todo: 这里感觉有点问题
        return self.request.get['pages']

    @property # 其他类可以访问
    def page_number(self):
        page_kwarg=self.page_kwarg
        page=self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        return page
    
    def get_queryset_cache_key(self):
        '''子类重写，获取queryset的缓存key'''
        raise NotImplementedError()

    def get_queryset_data(self):
        '''子类重写，获取queryset的数据'''
        raise NotImplementedError()

    def get_queryset_from_cache(self,cache_key):
        '''根据cache_key获取缓存数据
            不存在执行get_queryset_data
        '''
        value=cache.get(cache_key)
        if value:
            return value
        else:
            article_list=self.get_queryset_data()
            cache.get(cache_key,article_list)
            return article_list
        
    def get_queryset(self):
        '''获取cache_key
            从cache获取数据
        '''
        key=self.get_queryset_cache_key()
        value=self.get_queryset_from_cache(key)
        return value
    
    def get_context_data(self,**kwargs):
        kwargs['linktype']=self.link_type
        return super().get_context_data(**kwargs)

class IndexView(ArticleListView):
    '''首页'''
    link_type=LinkShowType.I
    def get_queryset_data(self):
        #获取发布的文章
        article_list=Article.objects.filter(type='a',status='p') 
        return article_list

    def get_queryset_cache_key(self):
        # cache_key='index_1
        cache_key='index_{page}'.format(page=self.page_number)
        return cache_key

class ArticleDetailView(DetailView):
    '''文章详情页面'''     
    template_name='blog/article_detail.html'
    model=Article
    pk_url_kwarg='article_id'
    context_object_name='article'

    def get_object(self,queryset=None):
        obj=super().get_object() # 获取article对象
        obj.viewed()
        self.object=obj
        return obj
     
    def get_context_data(self,**kwargs): # 渲染模板前调用，获取视图上下文数据
        comment_form=CommentForm()
        article_comments=self.object.commment_list() #从article获取评论列表
        parent_comments=article_comments.filter(parent_comment=None) # 没有父评论的评论
        blog_setting=get_blog_setting()
        paginator=Paginator(parent_comments,blog_setting.article_comment_count)
        page=self.request.GET.get('comment_page','1')
        if not page.isnumeric(): # 检查字符串是否只包含数字
            page=1
        else:
            page=int(page)
            if page<1:
                page=1
            if page>paginator.num_pages:
                page=paginator.num_pages
        p_comments=paginator.page(page)
        next_page=p_comments.next_page_number() if p_comments.has_next() else None
        prev_page=p_comments.previous_page_number if p_comments.has_previous() else None

        if next_page:
            kwargs['comment_next_page_url']=self.object.get_absolute_url()+f'?comment_page={next_page}#commentlist-container'
        if prev_page:
            kwargs['comment_prev_page_url']=self.object.get_absolute_url()+f'?comment_page={prev_page}#commentlist-container'
        kwargs['form']=comment_form
        kwargs['article_comments']=article_comments
        kwargs['p_comments']=p_comments
        kwargs['comment_count']=len(article_comments) if article_comments else 0
        kwargs['next_article']=self.object.next_article
        kwargs['prev_article']=self.object.prev_article

        return super().get_context_data(**kwargs)
    
class CategoryDetailView(ArticleListView):
    '''分类目录列表'''
    page_type='分类目录归档'

    def get_queryset_data(self):
        slug=self.kwargs['category_name']
        category=get_object_or_404(Category,slug=slug)
        categoryname=category.name
        self.categoryname=categoryname
        categorynames=list(map(lambda c:c.name,category.get_sub_categorys()))
        article_list=Article.objects.filter(category__name__in=categorynames,status='p')
        return article_list
    
    def get_queryset_cache_key(self):
        slug=self.kwargs['category_name']
        category=get_object_or_404(Category,slug=slug)
        categoryname=category.name
        self.categoryname=categoryname
        cache_key='category_list_{categoryname}_{page}'.format(categoryname=categoryname,page=self.page_number)
        return cache_key

    def get_context_data(self,**kwargs):
        categoryname=self.categoryname
        try:
            categoryname=categoryname.split('/')[-1]
        except Exception as e:
            print(e)
        kwargs['page_type']=CategoryDetailView.page_type
        kwargs['tag_name']=categoryname
        return super().get_context_data(**kwargs)
    
class AuthorDetailView(ArticleListView):
    '''作者详情页'''
    page_type='作者文章归档'

    def get_queryset_cache_key(self):
        from uuslug import slugify
        author_name=slugify(self.kwargs['author_name'])
        cache_key='author_{author_name}_{page}'.format(author_name=author_name,page=self.page_number)
        return cache_key
    
    def get_queryset_data(self):
        author_name=self.kwargs['author_name']
        article_list=Article.objects.filter(author__username=author_name,type='a',status='p')
        return article_list
    
    def get_context_data(self,**kwargs):
        author_name=self.kwargs['author_name']
        kwargs['page_type']=AuthorDetailView.page_type
        kwargs['tag_name']=author_name
        return super().get_context_data(**kwargs)
        
class TagDetailView(ArticleListView):
    '''标签列表页面'''
    page_type='分类标签归档'

    def get_queryset_data(self):
        slug=self.kwargs['tag_name']
        tag=get_object_or_404(Tag,slug=slug)
        tag_name=tag.name
        self.name=tag_name
        article_list=Article.objects.filter(tags__name=tag_name,type='a',status='p')
        return article_list
    
    def get_queryset_cache_key(self):
        slug=self.kwargs['tag_name']
        tag=get_object_or_404(Tag,slug=slug)
        tag_name=tag.name
        self.name=tag_name
        cache_key='tag_{tag_name}_{page}'.format(tag_name=tag_name,page=self.page_number) 
        return cache_key

    def get_context_data(self,**kwargs):
        tag_name=self.name
        kwargs['page_type']=TagDetailView.page_type
        kwargs['tag_name']=tag_name
        return super().get_context_data(**kwargs)
        
class ArchivesView(ArticleListView):
    '''文章归档页面'''
    page_type='文章归档'
    paginate_by=None
    page_kwarg=None
    template_name='blog/article_archives.html'

    def get_queryset_data(self):
        return Article.objects.filter(status='p').all()

    def get_queryset_cache_key(self):
        cache_key='archives'
        return cache_key
    
class LinkListView(ListView):
    model=Links
    template_name='blog/links_list.html'

    def get_queryset(self):
        '''获取数据'''
        return Links.objects.filter(is_enable=True)

#todo: essearch暂时不做

@csrf_exempt
def fileupload(request):
    #todo: 阉割掉的需要自己做
    pass

def page_not_found_view(request,exception,template_name='bolg/error_page.html'):
    url=request.get_full_path() # 获取请求的完整路径
    return render(request,template_name,{
        'message': _('Sorry, the page you requested is not found, please click the home page to see other?'),
        'statuscode': '404'},status=404)

def server_error_view(request,template_name='blog/error_page.html'):
    return render(request,template_name,{
        'message': _('Sorry, the server is busy, please click the home page to see other?'),
                   'statuscode': '500'},status=500)

def permission_denied_view(request,exception,template_name='blog/error_page.html'):
    return render(request,template_name,{
        'message': _('Sorry, you do not have permission to access this page?'),
        'statuscode': '403'},status=403)

def clean_cache_view(request):
    cache.clear()
    return HttpResponse('ok')




        


    










        



