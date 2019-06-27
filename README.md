# Flask学习
## 安装所需要的包
在PyCharm的Terminal里执行下面的命令\
pip install -r install.txt
## [数据库](https://github.com/luhuisicnu/The-Flask-Mega-Tutorial-zh/blob/master/docs/%E7%AC%AC%E5%9B%9B%E7%AB%A0%EF%BC%9A%E6%95%B0%E6%8D%AE%E5%BA%93.md)
### 初始化
Flask-Migrate通过flask命令暴露来它的子命令。 你已经看过flask run，这是一个Flask本身的子命令。 Flask-Migrate添加了flask db子命令来管理与数据库迁移相关的所有事情。 那么让我们通过运行flask db init来创建microblog的迁移存储库：

(venv) $ flask db init  
  Creating directory /home/miguel/microblog/migrations ... done  
  Creating directory /home/miguel/microblog/migrations/versions ... done  
  Generating /home/miguel/microblog/migrations/alembic.ini ... done  
  Generating /home/miguel/microblog/migrations/env.py ... done  
  Generating /home/miguel/microblog/migrations/README ... done  
  Generating /home/miguel/microblog/migrations/script.py.mako ... done  
  Please edit configuration/connection/logging settings in  
  '/home/miguel/microblog/migrations/alembic.ini' before proceeding.  
  
### 第一次数据库迁移
自动迁移将把整个User模型添加到迁移脚本中。 flask db migrate子命令生成这些自动迁移：  
(venv) $ flask db migrate -m "users table"  
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.  
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.  
INFO  [alembic.autogenerate.compare] Detected added table 'user'  
INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_email' on '['email']'  
INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_username' on '['username']'  
Generating /home/miguel/microblog/migrations/versions/e517276bb1c2_users_table.py ... done  
  
通过命令输出，你可以了解到Alembic在创建迁移的过程中执行了哪些逻辑。前两行是常规信息，通常可以忽略。   
之后的输出表明检测到了一个用户表和两个索引。 然后它会告诉你迁移脚本的输出路径。 e517276bb1c2是自动生  
成的一个用于迁移的唯一标识（你运行的结果会有所不同）。 -m可选参数为迁移添加了一个简短的注释。  

生成的迁移脚本现在是你项目的一部分了，需要将其合并到源代码管理中。 如果你好奇，并检查了它的代码，  
就会发现它有两个函数叫upgrade()和downgrade()。 upgrade()函数应用迁移，downgrade()函数回滚迁移。  
 Alembic通过使用降级方法可以将数据库迁移到历史中的任何点，甚至迁移到较旧的版本。  

flask db migrate命令不会对数据库进行任何更改，只会生成迁移脚本。 要将更改应用到数据库，  
必须使用flask db upgrade命令。

(venv) $ flask db upgrade  
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.  
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.  
INFO  [alembic.runtime.migration] Running upgrade  -> e517276bb1c2, users table  

因为本应用使用SQLite，所以upgrade命令检测到数据库不存在时，会创建它（在这个命令完成之后，你会注意到一个名为app.db的文件，  
即SQLite数据库）。 在使用类似MySQL和PostgreSQL的数据库服务时，必须在运行upgrade之前在数据库服务器上创建数据库。  

### 数据库升级和降级流程
目前，本应用还处于初期阶段，但讨论一下未来的数据库迁移战略也无伤大雅。 假设你的开发计算机上存有应用的源代码，并且还将其部署到生产服务器上，运行应用并上线提供服务。  

而应用在下一个版本必须对模型进行更改，例如需要添加一个新表。 如果没有迁移机制，这将需要做许多工作。无论是在你的开发机器上，还是在你的服务器上，都需要弄清楚如何变更你的数据库结构才能完成这项任务。  

通过数据库迁移机制的支持，在你修改应用中的模型之后，将生成一个新的迁移脚本（flask db migrate），你可能会审查它以确保自动生成的正确性，然后将更改应用到你的开发数据库（flask db upgrade）。 测试无误后，将迁移脚本添加到源代码管理并提交。  

当准备将新版本的应用发布到生产服务器时，你只需要获取包含新增迁移脚本的更新版本的应用，然后运行flask db upgrade即可。 Alembic将检测到生产数据库未更新到最新版本，并运行在上一版本之后创建的所有新增迁移脚本。  

正如我前面提到的，flask db downgrade命令可以回滚上次的迁移。 虽然在生产系统上不太可能需要此选项，但在开发过程中可能会发现它非常有用。 你可能已经生成了一个迁移脚本并将其应用，只是发现所做的更改并不完全是你所需要的。 在这种情况下，可以降级数据库，删除迁移脚本，然后生成一个新的来替换它。  


# 密码重置令牌
 这个计划中棘手的部分是确保只有有效的重置链接可以用来重置帐户的密码。

生成的链接中会包含令牌，它将在允许密码变更之前被验证，以证明请求重置密码的用户是通过访问重置密码邮件中的链接而来的。JSON Web Token（JWT）是这类令牌处理的流行标准。 JWTs的优点是它是自成一体的，不但可以生成令牌，还提供对应的验证方法。