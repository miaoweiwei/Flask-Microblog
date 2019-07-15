# Flask学习
## 安装所需要的包
[数据库设计工具](https://ondras.zarovi.cz/sql/demo/)  
在PyCharm的Terminal里执行下面的命令  
<code> 

    pip install -r install.txt  
</code>
导出该项目安装的包  
<code> 

    pip freeze > requirements.txt
</code>

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


# 国际化和本地化
### Flask-Babe 用于简化翻译工作
安装 (venv) $ pip install flask-babel  

Flask-Babel的初始化与之前的插件类似：  

app/__init__.py: Flask-Babel实例  
<code>  

    # ...
    from flask_babel import Babel
    
    app = Flask(__name__)
    # ...
    babel = Babel(app)
    
</code>

为了跟踪支持的语言列表，我将添加一个配置变量：  
config.py：支持的语言列表。
<code>

    class Config(object):
        # ...
        LANGUAGES = ['en', 'es']
</code>
我为本应用使用双字母代码来表示语言种类，但如果你需要更具体，还可以添加国家代码。 例如，你可以使用en-US，en-GB和en-CA来支持美国、英国和加拿大的英语以示区分。  

Babel实例提供了一个localeselector装饰器。 为每个请求调用装饰器函数以选择用于该请求的语言：
app/__init__.py：选择最匹配的语言。  
<code>

    from flask import request

    # ...
    
    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config['LANGUAGES'])
</code>  
这里我使用了Flask中request对象的属性accept_languages。 request对象提供了一个高级接口，用于处理客户端发送的带Accept-Language头部的请求。 该头部指定了客户端语言和区域设置首选项。 该头部的内容可以在浏览器的首选项页面中配置，默认情况下通常从计算机操作系统的语言设置中导入。 大多数人甚至不知道存在这样的设置，但是这是有用的，因为应用可以根据每个语言的权重，提供优选语言的列表。 为了满足你的好奇心，下面是一个复杂的Accept-Languages头部的例子：

Accept-Language: da, en-gb;q=0.8, en;q=0.7  

这表示丹麦语（da）是首选语言（默认权重= 1.0），其次是英式英语（en-GB），其权重为0.8，最后是通用英语（en），权重为0.7。  

要选择最佳语言，你需要将客户请求的语言列表与应用支持的语言进行比较，并使用客户端提供的权重，查找最佳语言。 这样做的逻辑有点复杂，但它已经全部封装在best_match()方法中了，该方法将应用提供的语言列表作为参数并返回最佳选择。

#### 标记文本以在Python源代码中执行翻译  
支持多语言的常规流程是在源代码中标记所有需要翻译的文本。 文本标记后，Flask-Babel将扫描所有文件，并使用gettext工具将这些文本提取到单独的翻译文件中。 不幸的是，这是一个繁琐的任务，并且是启用翻译的必要条件。

为翻译而标记文本的方式是将它们封装在一个函数调用中，该函数调用为_()，仅仅是一个下划线。最简单的情况是源代码中出现的字符串。下面是一个flask()语句的例子：

<code>

    from flask_babel import _
    # ...
    flash(_('Your post is now live!'))
</code>

_()函数用于原始语言文本（在这种情况下是英文）的封装。 该函数将使用由localeselector装饰器装饰的选择函数，来为给定客户端查找正确的翻译语言。 _()函数随后返回翻译后的文本，在本处，翻译后的文本将成为flash()的参数。

但是不可能每个情况都这么简单，试想如下的另一个flash()调用：

<code>

    flash('User {} not found.'.format(username))
</code>
该文本具有一个安插在静态文本中间的动态组件。 _()函数的语法支持这种类型的文本，但它基于旧版本的字符串替换语法：

<code>

    flash(_('User %(username)s not found.', username=username))
</code>

还有更难处理的情况。 有些字符串文字并非是在发生请求时分配的，比如在应用启动时。因此在评估这些文本时，无法知道要使用哪种语言。 一个例子是与表单字段相关的标签，处理这些文本的唯一解决方案是找到一种方法来延迟对字符串的评估，直到它被使用，比如有实际上的请求发生了。 Flask-Babel提供了一个称为lazy_gettext()的_()函数的延迟评估的版本：

<code>

    from flask_babel import lazy_gettext as _l
    
    class LoginForm(FlaskForm):
        username = StringField(_l('Username'), validators=[DataRequired()])
        # ...
</code>

正在导入的这个翻译函数被重命名为_l()，以使其看起来与原始的_()相似。 这个新函数将文本包装在一个特殊的对象中，这个对象会在稍后的字符串使用时触发翻译。

Flask-Login插件只要将用户重定向到登录页面，就会闪现消息。 此消息为英文，来自插件本身。 为了确保这个消息也能被翻译，我将重写默认消息，并用_l()函数进行延迟处理：

<code>

    login = LoginManager(app)
    login.login_view = 'login'
    # 默认的登录提示信息使用 _l() 函数来翻译提示信息
    login.login_message = _l('Please log in to access this page.')
</code>

#### 标记文本以在模板中进行翻译
_()函数也可以在模板中使用，所以过程非常相似。 例如，参考来自404.html的这段HTML代码：
<code>

    <h1>File Not Found</h1>
</code>

启用翻译之后的版本是：
<code>

    <h1>{{ _('File Not Found') }}</h1>
</code>

请注意，除了用_()包装文本外，还需要添加{{...}}来强制_()进行翻译，而不是将其视为模板中的文本字面量。

对于具有动态组件的更复杂的短语，也可以使用参数：  
<code>

    <h1>{{ _('Hi, %(username)s!', username=current_user.username) }}</h1>
</code>

一旦应用所有_()和_l()都到位了，你可以使用pybabel命令将它们提取到一个*.pot文件中，该文件代表可移植对象模板*。这是一个文本文件，其中包含所有标记为需要翻译的文本。 这个文件的目的是作为一个模板来为每种语言创建翻译文件。

提取过程需要一个小型配置文件，告诉pybabel哪些文件应该被扫描以获得可翻译的文本。 下面你可以看到我为这个应用创建的babel.cfg：

babel.cfg：PyBabel配置文件。 

<code>
    
    [python: app/**.py]
    [jinja2: app/templates/**.html]
    extensions=jinja2.ext.autoescape,jinja2.ext.with_
</code>

前两行分别定义了Python和Jinja2模板文件的文件名匹配模式。 第三行定义了Jinja2模板引擎提供的两个扩展，以帮助Flask-Babel正确解析模板文件。

可以使用以下命令来将所有文本提取到* .pot *文件：

<code>

    (venv) $ pybabel extract -F babel.cfg -k _l -o messages.pot .
</code>

pybabel extract命令读取-F选项中给出的配置文件，然后从命令给出的目录（当前目录或本处的. ）(这个点不能少，这个点表示当前目录)扫描与配置的源匹配的目录中的所有代码和模板文件。 默认情况下，pybabel将查找_()以作为文本标记，但我也使用了重命名为_l()的延迟版本，所以我需要用-k _l来告诉该工具也要查找它 。 -o选项提供输出文件的名称。

我应该注意，messages.pot文件不需要合并到项目中。 这是一个只要再次运行上面的命令，就可以在需要时轻松地重新生成的文件。 因此，不需要将该文件提交到源代码管理。

### 生成语言目录

该过程的下一步是在除了原始语言（在本例中为英语）之外，为每种语言创建一份翻译。 我要从添加西班牙语（语言代码es）开始，所以这样做的命令是：

<code>

    (venv) $ pybabel init -i messages.pot -d app/translations -l es
    creating catalog app/translations/es/LC_MESSAGES/messages.po based on messages.pot
</code>

### 命令行增强

在编辑好 app/cli.py 后 因为 FLASK_APP 默认为 FLASK_APP=hello.py,所以要先执行set FLASK_APP=run.py,然后在执行 flask --help 查看
命令是否注册就会显示注册成功。注意使用PyCharm创建flask项目时会一起创建一个app.py.如果cli引入到app.py的使用上面的方法不行。
cli要引入到其他的文件，可以另外新建一个run.py文件，把app,cli引入到其中,在使用命令 set FLASK_APP=run.py 和  flask --help 
引入成功，执行命令
<code>
    
    flask translate init zh #创建一个中文的翻译文件
    flask translate update # 用于更新所有语言存储库
    flask translate compile # 用于编译所有语言存储库
</code>
