import os
from apps import create_app, db
from flask_migrate import MigrateCommand # flask 迁移数据
from flask_script import Manager

env = os.environ.get('WEBAPP_ENV', 'dev')
app = create_app('config.%sConfig' % env.capitalize())
manager = Manager(app)

# 向manager对象中添加数据库的操作命令
# 第一个参数是给这条命令取的名字叫什么,关于数据库的我们通常叫db
# 第二个参数就是具体的命令
manager.add_command('db', MigrateCommand)

#创建数据库脚本
@manager.command
def create_db():
    db.create_all()


if __name__ == '__main__':
    manager.run()