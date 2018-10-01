from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

from taggit.managers import TaggableManager

# Create your models here.
class PublishedManager(models.Manager):
    """docstring for PublishedManager."""
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):
    """Django data model Post"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # models managers
    objects = models.Manager() ## THe default manager.
    published = PublishedManager()  ## Custom manager to published post only.
    tags = TaggableManager()

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering=('-publish',)

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.publish.year,
                                                self.publish.month,
                                                self.publish.day,
                                                self.slug])

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Django data model Comment"""
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)
