#!/usr/bin/env python
# coding=utf8

try:
    import psyco

    psyco.full()
except:
    pass
import tornado

from handlers import BaseHandler, AdminBaseHandler
from models import Post, Category, Tag, User, Link
from lib.pagination import Pagination


class IndexHandler(AdminBaseHandler):
    def get(self):
        self.render('admin/index.html')


class CategoryHandler(AdminBaseHandler):
    def get(self):
        self.render('admin/category/index.html', categories=Category.select(), nav='category')


class CateHandler(AdminBaseHandler):
    def post(self):
        name = self.get_argument('name', None)
        slug = self.get_argument('slug', None)
        q = Category.select().where(Category.name == name)
        if q.count() > 0:
            self.flash('cateegory exists!')
            self.render('admin/category/add.html')
            return
        else:
            Category.create(name=name, slug=slug)
            self.redirect('/admin/category')


class PostsHandler(AdminBaseHandler):
    def get(self, page=1):
        posts = Pagination(Post.select(), int(page), 10)
        self.render('admin/post/index.html', pagination=posts, nav='post')


class PostHandler(AdminBaseHandler):
    def get(self):
        self.render('admin/post/add.html', category=Category.select(), nav='post')

    def post(self):
        title = self.get_argument('title', None)
        slug = self.get_argument('slug', '')
        category_id = self.get_argument('category', 1)
        content = self.get_argument('content', '')
        tag = self.get_argument('tag', None)

        category = Category.get(id=int(category_id))
        post = Post.create(title=title, category=category, slug=slug, content=content, tags=tag)

        if tag:
            for tag in post.taglist():
                Tag.create(name=tag, post=post.id)
        self.render('admin/post/add.html')


class PostUpdateHandler(AdminBaseHandler):
    def get(self, postid):
        try:
            post = Post.get(id=postid)
        except Post.DoesNotExist:
            raise tornado.web.HTTPError(404)

        category = Category.select()
        self.render('admin/post/update.html', post=post, category=category)

    def post(self, postid):
        title = self.get_argument('title', None)
        slug = self.get_argument('slug', '')
        category_id = self.get_argument('category', 1)
        content = self.get_argument('content', '')
        tags = self.get_argument('tag', '')
        category = Category.get(id=int(category_id))

        Post.update(title=title, slug=slug,
                    category=category, content=content, tags=tags).where(Post.id == postid).execute()

        tag_list = set(tags.split(","))
        if tag_list:
            for tag in tag_list:
                try:
                    Tag.get(name=tag, post=postid)
                except Tag.DoesNotExist:
                    Tag.create(name=tag, post=postid)
        self.redirect('/admin/posts')
        return


class PostDeleteHandler(AdminBaseHandler):
    def get(self, postid):
        Post.delete().where(Post.id == postid).execute()
        Tag.delete().where(Tag.post == postid).execute()
        self.redirect('/admin/posts')
        return


class UsersHandler(AdminBaseHandler):
    def get(self):
        return self.render('admin/user/index.html', users=User.select(), nav='user')


class CommentsHandler(AdminBaseHandler):
    def get(self):
        self.render('admin/comment/comment.html')


class LinksHandler(AdminBaseHandler):
    def get(self, page=1):
        pagination = Pagination(Link.select(), int(page), 1)
        self.render('admin/link/index.html', pagination=pagination, nav='link')

    def post(self):
        name = self.get_argument('name', None)
        url = self.get_argument('url')
        if name and url:
            Link.create(name=name, url=url)
        self.redirect('/admin/links')


routes = [
    (r'/admin', IndexHandler),
    (r'/admin/posts', PostsHandler),
    (r'/admin/posts/(\d+)', PostsHandler),
    (r'/admin/post/add', PostHandler),
    (r'/admin/post/(\d+)/update', PostUpdateHandler),
    (r'/admin/post/(\d+)/delete', PostDeleteHandler),
    (r'/admin/category', CategoryHandler),
    (r'/admin/category/add', CateHandler),
    (r'/admin/users', UsersHandler),
    (r'/admin/links', LinksHandler),
    (r'/admin/links/(\d+)', LinksHandler),
]