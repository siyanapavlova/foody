from flask import render_template, flash, redirect, request
from app import app
from .forms import LoginForm, NextMessage
from test import chat

message_list = []
intent = []
context = {}

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname':'Siyana'}
    posts = [
        {
            'author': {'nickname':'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname':'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',
                            title='Home',
                            user=user,
                            posts=posts)

@app.route('/login',methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="%s", remember_me=%s' %
              (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html',
                            title='Sign In',
                            form=form,
                            providers=app.config['OPENID_PROVIDERS'])

@app.route('/message', methods=['GET', 'POST'])
def message():
    global intent
    global context
    message = "hello"
    if request.method == "POST":
        message = request.form['mytext']
        message_list.append({'sender':'you','message':message})
    context, intent, output, response = chat(context, message, intent)
    message_list.append({'sender':'me','message':response})
    return render_template('message.html',
                            message=message,
                            message_list=message_list)
