# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################


response.logo = A(B('boot',SPAN('UP')),XML('&trade;&nbsp;'),
                  _class="brand",_href=URL('BootUP', 'default', 'index'))
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Y8191122'
response.meta.keywords = 'web2py, python, framework, bootUP'
response.meta.generator = 'Web2py Web Framework BootUP'

## your http://google.com/analytics id
response.google_analytics_id = None

#The search form to be put on every page
searchForm = FORM(INPUT(_type='search', _placeholder='Search', _name='searchBox'),
                  SELECT(['All'] + bootableCategories, _name='cat'),
                  INPUT(_type='submit', _value='Search', _name='searchSubmit'),
                  _name='searchForm',
                  _class='form-inline',
                  _id='searchForm')

#URL of login page, this is used in multiple places, hence why it is defined here
response.loginURL = URL('BootUP', 'users', 'user', args=['login'])

#The main application menu
response.menu = [
    (T('Create Bootable'), False, URL('BootUP', 'bootables', 'create')),
    ('Search:', False, searchForm)

]

#User menu, changes depending on user status
if session.user is None:
    response.user_menu = [
        (T('Log in'), False, response.loginURL),
        (T('Sign Up'), False, URL('BootUP', 'users', 'user', args=['register']))
    ]
else:
    response.user_menu = []
    #If user owns bootables, give link to boot manager dashboard
    if db(db.Bootables.userID == session.user).count() > 0:
        response.user_menu += [
            (T('Bootable Dashboard'), False, URL('BootUp', 'bootables', 'dash'))
        ]

    response.user_menu += [
        (T('View Profile'), False, URL('BootUP', 'users', 'profile')),
        (T('Log out'), False, URL('BootUP', 'users', 'user', args=['logout']))
    ]


#If search has been preformed redirect to search page
if searchForm.accepts(request.post_vars, session, formname='searchForm'):
    redirect(URL('default', 'search', vars=dict(search=request.post_vars.searchBox,
                                                cat=request.post_vars.cat)))

#Include dev menues
DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu += [
        (SPAN('web2py', _class='highlighted'), False, 'http://web2py.com', [
        (T('My Sites'), False, URL('admin', 'default', 'site')),
        (T('This App'), False, URL('admin', 'default', 'design/%s' % app), [
        (T('Controller'), False,
         URL(
         'admin', 'default', 'edit/%s/controllers/%s.py' % (app, ctr))),
        (T('View'), False,
         URL(
         'admin', 'default', 'edit/%s/views/%s' % (app, response.view))),
        (T('Layout'), False,
         URL(
         'admin', 'default', 'edit/%s/views/layout.html' % app)),
        (T('Stylesheet'), False,
         URL(
         'admin', 'default', 'edit/%s/static/css/web2py.css' % app)),
        (T('DB Model'), False,
         URL(
         'admin', 'default', 'edit/%s/models/db.py' % app)),
        (T('Menu Model'), False,
         URL(
         'admin', 'default', 'edit/%s/models/menu.py' % app)),
        (T('Database'), False, URL(app, 'appadmin', 'index')),
        (T('Errors'), False, URL(
         'admin', 'default', 'errors/' + app)),
        (T('About'), False, URL(
         'admin', 'default', 'about/' + app)),
        ]),
            ('web2py.com', False, 'http://www.web2py.com', [
             (T('Download'), False,
              'http://www.web2py.com/examples/default/download'),
             (T('Support'), False,
              'http://www.web2py.com/examples/default/support'),
             (T('Demo'), False, 'http://web2py.com/demo_admin'),
             (T('Quick Examples'), False,
              'http://web2py.com/examples/default/examples'),
             (T('FAQ'), False, 'http://web2py.com/AlterEgo'),
             (T('Videos'), False,
              'http://www.web2py.com/examples/default/videos/'),
             (T('Free Applications'),
              False, 'http://web2py.com/appliances'),
             (T('Plugins'), False, 'http://web2py.com/plugins'),
             (T('Layouts'), False, 'http://web2py.com/layouts'),
             (T('Recipes'), False, 'http://web2pyslices.com/'),
             (T('Semantic'), False, 'http://web2py.com/semantic'),
             ]),
            (T('Documentation'), False, 'http://www.web2py.com/book', [
             (T('Preface'), False,
              'http://www.web2py.com/book/default/chapter/00'),
             (T('Introduction'), False,
              'http://www.web2py.com/book/default/chapter/01'),
             (T('Python'), False,
              'http://www.web2py.com/book/default/chapter/02'),
             (T('Overview'), False,
              'http://www.web2py.com/book/default/chapter/03'),
             (T('The Core'), False,
              'http://www.web2py.com/book/default/chapter/04'),
             (T('The Views'), False,
              'http://www.web2py.com/book/default/chapter/05'),
             (T('Database'), False,
              'http://www.web2py.com/book/default/chapter/06'),
             (T('Forms and Validators'), False,
              'http://www.web2py.com/book/default/chapter/07'),
             (T('Email and SMS'), False,
              'http://www.web2py.com/book/default/chapter/08'),
             (T('Access Control'), False,
              'http://www.web2py.com/book/default/chapter/09'),
             (T('Services'), False,
              'http://www.web2py.com/book/default/chapter/10'),
             (T('Ajax Recipes'), False,
              'http://www.web2py.com/book/default/chapter/11'),
             (T('Components and Plugins'), False,
              'http://www.web2py.com/book/default/chapter/12'),
             (T('Deployment Recipes'), False,
              'http://www.web2py.com/book/default/chapter/13'),
             (T('Other Recipes'), False,
              'http://www.web2py.com/book/default/chapter/14'),
             (T('Buy this book'), False,
              'http://stores.lulu.com/web2py'),
             ]),
            (T('Community'), False, None, [
             (T('Groups'), False,
              'http://www.web2py.com/examples/default/usergroups'),
                        (T('Twitter'), False, 'http://twitter.com/web2py'),
                        (T('Live Chat'), False,
                         'http://webchat.freenode.net/?channels=web2py'),
                        ]),
                (T('Plugins'), False, None, [
                        ('plugin_wiki', False,
                         'http://web2py.com/examples/default/download'),
                        (T('Other Plugins'), False,
                         'http://web2py.com/plugins'),
                        (T('Layout Plugins'),
                         False, 'http://web2py.com/layouts'),
                        ])
                ]
         )]
if DEVELOPMENT_MENU: _()

