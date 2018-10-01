from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.db.models import Count

from taggit.models import Tag

from.forms import EmailPostForm, CommentForm, SearchForm
from .models import Post, Comment


# Create your views here.
def post_home(request):
    template = "blog/home.html"
    context = {}

    return render(request, template, context)

def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 5) ## 5 posts in each page
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        ## if page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        ## if page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    template = "blog/post/list.html"
    context = {'posts': posts,
                'page': page,
                'tag': tag}

    return render(request, template, context)

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                    status="published",
                                    publish__year=year,
                                    publish__month=month,
                                    publish__day=day
                                    )

    # List of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == "POST":
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    print(similar_posts)
    template = "blog/post/detail.html"
    context = {'post': post,
                'comments': comments,
                'new_comment': new_comment,
                'comment_form': comment_form,
                'similar_posts': similar_posts
                }

    return render(request, template, context)

def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        #Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #Form fields passed validation
            cd = form.cleaned_data
            # send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    template = "blog/post/share.html"
    context = {'post': post,
                'form': form,
                'sent': sent}

    return render(request, template, context)

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            # results = Post.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank') ## ranking based search
            results = Post.objects.annotate(similarity=TrigramSimilarity('title', query),).filter(similarity__gt=0.3).order_by('-similarity') ## TrigramSimilarity searching algorithm

    template = "blog/post/search.html"
    context = {'form': form,
                'query': query,
                'results': results}

    return render(request, template, context)

# class based views
# class PostListView(ListView):
#     """docstring for PostListView."""
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 5
#     template_name = 'blog/post/list.html'
