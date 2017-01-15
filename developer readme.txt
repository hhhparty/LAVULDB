1.迁移数据库migration db
数据库迁移工具可以方便的更新数据模型。
在维护数据库迁移之前，首先要使用init命令创建迁移仓库：
（venv）$python managy.py db init
然后运行下列命令,-m 后面是对此次操作的署名
（venv）$python managy.py  db migrate -m "inital migration"
第三步是运行下列命令，进行表的创建或更新。
（venv）$python managy.py db upgrade
之后修改数据库模式后，可以使用下列命令更新数据库结构
（venv）$python managy.py db upgrade

若要检查是否真的创建了表，可以在运行下列sqlite命令
 （venv）$sqlite3 data-dev.sqlite 
  sqlite> .tables
2.运行测试用例
写好测试用例后，可以运行下列命令执行测试：
（venv）$python manage.py test

3.填写requirements.txt使用下列命令
（venv）$pip freeze > requirements.txt
在发布前，要创建整个虚拟环境的副本，可以用该文件简单创建副本，届时只需运行下列命令
（venv）$pip install -r requirements.txt
