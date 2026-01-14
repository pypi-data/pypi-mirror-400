# 配置加载类使用说明

为部署的应用提供统一的配置文件解析接口。根据不同的应用名称生成不同的配置文件路径。并将其配置文件加载。

对一个应用`appname`，在Linux操作系统下，配置文件路径依次为

* /etc/`appname`.ini
* ${HOME}/etc/`appname`.ini
* ${PROJECT_HOME}/etc.ini

在Windows下，配置文件的路径依次为

* %ProgramData%/`appname`.ini
* %APPDATA%/`appname`.ini
* %PROJECT_HOME%/etc.ini

其中第三个路径为测试用的路径。后面的配置文件覆盖前面的配置。

## 类说明

该包提供类`ConfigDict`。其初始化函数接收一个参数`appname`。包含一个帮助方法`self.show()`，用以查看当前应用的配置文件路径。初始化完成后，`ConfigDict`的对象实例自动加载了所有的配置文件，以字典的形式存储在对象中。

```python

config = ConfigDict(appname='app')
config.show()
print(config)

```
