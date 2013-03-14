""" Basic blog using webpy 0.3 """
import web
import model

from auth import DBAuth


### Url mappings



urls = (
    '/', 'Index',
    '/view/(\d+)', 'View',
    '/new', 'New',
    '/delete/(\d+)', 'Delete',
    '/edit/(\d+)', 'Edit',
    '/logout', 'Logout',
    '/vote/(\d+)/(\d+)', 'Vote',
    '/deletevote/(\d+)', 'Deletevote',
    '/addaccount', 'AddAccount',
    '/jsonpdemo', 'JsonpDemo',
)


### Templates

t_globals = {
    'datestr': web.datestr
}
render = web.template.render('/var/www/webapp/templates', globals=t_globals)

app = web.application(urls, globals(),autoreload=False)
main = app.wsgifunc()

db = web.database(dbn='mysql', db='blog', user='root', pw='MnEmn0Ck')
mysession = web.session.Session(app, web.session.DiskStore('/var/www/webapp/sessions'))

settings = dict(
    template_login = render.login,
    template_reset_token = render.reset_token,
    template_reset_email = render.reset_email,
    template_reset_change = render.reset_change,
    #url_reset_token = '/appcode.py/password_reset',
    #url_reset_change = '/appcode.py/password_reset',
)

auth = DBAuth(app, db, mysession, **settings)

t_globals = {
    'datestr': web.datestr,
    'auth':    auth,
    'model':   model
}

render = web.template.render('/var/www/webapp/templates/', base='base', globals=t_globals)
renderInsert = web.template.render('/var/www/webapp/templates/', globals=t_globals)

class Index:
    def GET(self):
        """ Show page """
        posts = model.get_posts()
        return render.index(posts,auth.getUser())


class View:
    form = web.form.Form(
        web.form.Textbox('title', web.form.notnull,
            size=30,
            description="Comment title:"),
        web.form.Textarea('content', web.form.notnull,
            rows=30, cols=80,
            description="Comment content:"),
        web.form.Button('Post Comment'),
    )

    def GET(self, id):
        """ View single post """
	# TODO: make the post test render as htmnl
        post = model.get_post(int(id))
        user = model.getUserById(post.user_id)
        comments = model.get_comments(int(id))
        renderedComments = ""
        if comments:
            renderedComments = renderInsert.comments(comments,model) 
        votes = model.get_votes(id)    
	lUser = auth.getUser()
        if lUser:
            hasUserVoted = model.hasUserVoted(auth.getUser().user_id,post.id)
        else:
            hasUserVoted = False
        return render.view(post,user,renderedComments,self.form,hasUserVoted,votes)
    @auth.protected()
    def POST(self,refId):
        form = self.form

        if not form.validates():
            return render.view(form)
        model.new_post(form.d.title, form.d.content, auth.getUser().user_id, refId)
        raise web.seeother('/')

class New:
    form = web.form.Form(
        web.form.Textbox('title', web.form.notnull, 
            size=30,
            description="Post title:"),
        web.form.Textarea('content', web.form.notnull, 
            rows=30, cols=80,
            description="Post content:"),
        web.form.Button('Post entry'),
    )
    title="New Post"
    @auth.protected()
    def GET(self):
        form = self.form()
        return render.form(form,self.title)
    @auth.protected()    
    def POST(self):
        form = self.form()
	
        if not form.validates():
            return render.form(form,self.title)
        model.new_post(form.d.title, form.d.content, auth.getUser().user_id)
        raise web.seeother('/')

class AddAccount:
    form = web.form.Form(
        web.form.Textbox('username', web.form.notnull,
            size=30,
            description="User Name:"),
        web.form.Textbox('email', web.form.notnull,
            size=30,
            description="Email:"),
        web.form.Password('password', web.form.notnull,
            size=30,
            description="Password:"),
        web.form.Button('Submit'),
    )
    title="Add Account"
    @auth.protected()
    def GET(self):
        form = self.form()
        return render.form(form,self.title)
    @auth.protected()
    def POST(self):
        form = self.form()

        if not form.validates():
            return render.form(form,self.title)
        auth.createUser(form.d.username, password=form.d.password, user_email=form.d.email, perms=[])

        raise web.seeother('/')

class Delete:
    @auth.protected()
    def POST(self, id):
	thisPost = model.get_post(int(id))
        thisUser = auth.getUser()
        if (thisPost.user_id == thisUser.user_id):
             model.del_post(int(id))
        raise web.seeother('/')


class Edit:
    @auth.protected()
    def GET(self, id):
        post = model.get_post(int(id))
        form = New.form()
        form.fill(post)
        return render.edit(post,form)


    def POST(self, id):
        form = New.form()
        post = model.get_post(int(id))
         
        if not form.validates():
            return render.edit(post, form)
        if (post.user_id == auth.getUser().user_id):
             model.update_post(int(id), form.d.title, form.d.content)
        raise web.seeother('/')

class Vote:
    @auth.protected()
    def GET(self, id, polarity):
        if not model.hasUserVoted(auth.getUser().user_id,id):
            model.vote(polarity,auth.getUser().user_id,id)
        origPost = model.getOrigional(id)
        raise web.seeother('/view/'+str(origPost))

class Deletevote:
    @auth.protected()
    def GET(self, id):
        if model.hasUserVoted(auth.getUser().user_id,id):
            model.delete_vote(auth.getUser().user_id,id)
	origPost = model.getOrigional(id)
        raise web.seeother('/view/'+str(origPost))


class Logout:
    def GET(self):
        auth.logout()
        raise web.seeother('/')

if __name__ == '__main__':
    app.run()

