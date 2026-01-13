# -*- coding: utf-8 -*-
from fastcodedog.generation.api.config import Config
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.text import Text
from fastcodedog.generation.base.variable import Variable


class Db(File):
    def __init__(self, comment=None, possible_imports: list | str = None, parent=None):
        super().__init__('db',
                         file_path=LocationFinder.get_path('db', 'model'),
                         package=LocationFinder.get_package('db', 'model'), comment=comment, parent=parent)
        self._init_blocks_and_imports()

    def _init_blocks_and_imports(self):
        self.blocks.append(Variable('engine', value=f"""create_engine(database_url, pool_size=pool_size, max_overflow=max_overflow, connect_args={{"check_same_thread": False}}
                       ) if database_url.startswith('sqlite') else create_engine(database_url)""",
                                    possible_imports=['from sqlalchemy import create_engine',
                                                      Import('database_url', Config().package),
                                                      Import('pool_size', Config().package),
                                                      Import('max_overflow', Config().package)]))
        self.blocks.append(Variable('Session', value='sessionmaker(bind=engine)',
                                    possible_imports=['from sqlalchemy.orm import sessionmaker']))
        get_session = Function('get_session', comment="""生成器方式获取数据库会话（主要适用于依赖注入场景）。

工作原理：
    1. 函数被调用时，创建一个新的Session实例。
    2. 通过 `yield session` 返回会话实例，并暂停执行。
    3. 当调用方结束会话使用（如请求结束），函数恢复执行，进入 `finally` 块，自动关闭会话。

使用方式1 (FastAPI 依赖注入，推荐):
    @app.get("/users")
    def get_users(session: Session = Depends(get_session)):
        return session.query(User).all()
    # 在这种情况下，FastAPI的Depends会自动处理生成器的迭代（即调用next()）和会话的关闭。

使用方式2 (手动调用，不推荐用于常规业务):
    # 警告：此方式需要手动管理会话的关闭，非常容易出错！
    gen = get_session()
    session = next(gen)  # 使用next()从生成器中获取会话实例
    try:
        # ... 使用 session ...
    finally:
        # 必须再次调用next()以触发finally块中的session.close()
        try:
            next(gen)
        except StopIteration:
            pass  # 捕获迭代结束的异常

注意事项:
    - 该函数返回的是一个生成器对象，而非直接的Session实例。
    - 在依赖注入之外的场景手动使用时，必须配合`next()`和`try...finally`结构，以确保会话被关闭。
    - 强烈建议优先使用依赖注入方式，避免手动操作`next()`。""")
        get_session.blocks.append(Text(f"""session = Session()
try:
    yield session
finally:
    session.close()"""))
        self.blocks.append(get_session)

        open_session = Function('open_session', decorators=[Function.Decorator('contextmanager', possible_imports='from contextlib import contextmanager')], comment="""上下文管理器方式获取数据库会话（适用于手动控制场景，如脚本、后台任务）。

工作原理：
    1. 被`@contextmanager`装饰后，该函数成为一个上下文管理器。
    2. 当使用`with`语句时，它会在进入块时执行`yield`之前的代码（创建会话），
       在退出块时执行`yield`之后的代码（关闭会话）。

使用方式 (必须配合 with 语句):
    with open_session() as session:
        user = session.query(User).get(1)
        session.add(User(name="new user"))
        session.commit()
    # with块结束时，会话会被自动关闭，无需手动操作。

与 next() 的关系:
    - **不需要手动调用`next()`**。`with`语句会自动处理上下文管理器的内部逻辑，
      包括触发生成器和管理资源生命周期。
    - 虽然其内部实现依赖于生成器，但`@contextmanager`装饰器已经封装了`next()`的调用细节。

注意事项:
    - 必须配合`with`语句使用，否则无法正确管理会话的生命周期。
    - 这种方式既安全又简洁，是手动控制会话场景下的最佳实践。""")
        open_session.blocks.append(Text(f"""session = Session()
try:
    yield session
finally:
    session.close()"""))
        self.blocks.append(open_session)
