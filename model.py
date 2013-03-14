import web, datetime

db = web.database(dbn='mysql', db='blog', user='root', pw='MnEmn0Ck')

def get_posts():
    query = 'select (select count(*) from votes where vote_entry_id=e.id and polarity = true) as upvotes, (select count(*) from votes where vote_entry_id=e.id and polarity = false)  as downvotes, e.id,e.title,e.posted_on,e.user_id,e.content,u.user_login,(select count(*) from entries as e2 where e2.ref = e.id) as comments from entries as e join user as u on u.user_id = e.user_id where e.ref is NULL order by e.posted_on desc;'
    return db.query(query)

def get_post(id):
    try:
        return db.select('entries', where='id=$id', vars=locals())[0]
    except IndexError:
        return None

def getOrigional(id):
    post = get_post(id)
    if post.ref:
        return post.ref
    return post.id

def get_votes(id):
    query = 'select count(v.polarity) as upvotes, (select count(v2.polarity) from votes as v2 where v2.vote_entry_id='+str(id)+' and v2.polarity = false) as downvotes from votes as v where v.vote_entry_id='+str(id)+' and v.polarity = TRUE'
    try:
        return db.query(query)[0]
    except IndexError:
        return None


def get_comments(orig_id):
    query = 'select (select count(*) from votes where vote_entry_id=e.id and polarity = true) as upvotes, (select count(*) from votes where vote_entry_id=e.id and polarity = false) as downvotes, e.id,e.title,e.posted_on,e.user_id,e.content,u.user_login from entries as e join user as u on u.user_id = e.user_id where ref='+str(orig_id)+' order by e.posted_on desc'
    return db.query(query)

def get_comment_count(orig_id):
    query = 'select count(*) from entries where ref='+str(orig_id)
    return db.query(query)

def vote(polarity, userid, voteid):
    db.insert('votes', polarity=polarity, vote_entry_id=voteid, vote_user_id=userid);

def delete_vote(userid, voteid):
    db.delete('votes', where='vote_user_id='+str(userid)+' AND vote_entry_id = '+voteid);

def new_post(title, text, userid, ref=None):
    db.insert('entries', title=title, content=text, posted_on=datetime.datetime.utcnow(), user_id=userid, ref=ref)

def del_post(id):
    db.delete('entries', where="id=$id", vars=locals())

def update_post(id, title, text):
    db.update('entries', where="id=$id", vars=locals(),
        title=title, content=text)

def getUserById(id):
    try:
        return db.select('user', where='user_id=$id', vars=locals())[0]
    except IndexError:
        return None

def hasUserVoted(userId,postId):
    try:
        return db.select('votes', where='vote_user_id=$userId and vote_entry_id=$postId', vars=locals())[0]
    except IndexError:
        return False 


        
