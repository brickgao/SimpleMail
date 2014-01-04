SimpleMail
=========

SimpleFTP 是一个由 Python 编写的带 GUI 的简易邮件客户端。

**Tips**: SimpleMail 是从 socket 层面完成的 SMTP 和 POP3 协议，目的在于学习 SMTP 和 POP3 协议，如果你需要用于生产环境，建议使用`smtplib`、`poplib`或者其他模块。

依赖
----

你可以在 [Python.org](python.org) 上获取 Python

在 [Riverbank](http://www.riverbankcomputing.co.uk/software/pyqt/intro) 上获取 PyQt

结构
----

`smtp.py`是 smtp 模块部分（仅实现通过 LOGIN 来 AUTH），`pop3.py`是 pop3 模块部分。

`ui.py`是 gui 模块部分，将`logging`中的`logger`定向输出至`QTextBrowser`，为了保证线程安全，更新由信号触发。

使用
----

通过`python main.py`启动，适用于 SMTP 认证为 LOGIN 的服务器。

日志
----


协议
----

[GPL](http://www.gnu.org/licenses/gpl.html)

