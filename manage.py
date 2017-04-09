#! python
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 09:50:00 2017

@author: leo
"""
import os
from app import create_app,db
from app.models import User,Role,Post,Comment,Vulninfo,Vulntype,Vulnref
from app.models import Cncpe,Vulnseverity,Vulnsoftwarelist
from app.webscrapy import Cnnvdvulninfo
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand


     
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)
cnnvd = Cnnvdvulninfo()

def make_shell_context():
    return dict(app=app, cnnvd=cnnvd,db=db, User=User, \
        Role=Role,Post=Post,Comment=Comment,Vulninfo=Vulninfo, \
        Vulntype=Vulntype,Vulnref=Vulnref,Cncpe=Cncpe, \
        Vulnseverity=Vulnseverity,Vulnsoftwarelist=Vulnsoftwarelist)
    
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Run the unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()

 

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from app.models import Role, User,Vulntype,Vulnseverity

    # migrate database to latest revision
    upgrade()

    # create user roles
    Role.insert_roles()

    # create self-follows for all users
    #User.add_self_follows()
    
    Vulntype.insert_vulntypes()
    Vulnseverity.insert_vulnseverity()
    User.add_superuser()


if __name__ == '__main__':
    manager.run()