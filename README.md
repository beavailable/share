# share
这是一个基于 HTTP 协议的文件分享工具，单文件开箱即用。

# 特性
- 跨平台
- 响应式布局
- 支持共享文件和文本
- 支持上传和下载
- 支持范围请求
- 支持密码分享
- 支持 IPv6

# 用法
```
usage: share.py [-b ADDRESS] [-p PORT] [-s] [-r] [-a] [-t] [-P [PASSWORD]] [-h] [--certfile CERTFILE] [--keyfile KEYFILE] [--keypass KEYPASS] [arguments ...]

positional arguments:
  arguments             a directory, files or texts

general options:
  -b ADDRESS, --bind ADDRESS
                        bind address [default: all interfaces]
  -p PORT, --port PORT  port [default: 8888]
  -s, --share           share mode (default mode)
  -r, --receive         receive mode, can be used with -s option (only for directory)
  -a, --all             show all files, including hidden ones, only for directory
  -t, --text            for text
  -P [PASSWORD], --password [PASSWORD]
                        access password, if no PASSWORD is specified, the environment variable SHARE_PASSWORD will be used
  -h, --help            show this help message and exit

tls options:
  --certfile CERTFILE   cert file
  --keyfile KEYFILE     key file
  --keypass KEYPASS     key password
```

# 截图
![img](https://github.com/beavailable/share/blob/main/screenshot.gif)

# 提示
- 如果你只有一个文件需要分享，下面这个简化的 url 可以帮助你快速访问到这个文件：
    ```
    http://{host}:{port}/file
    ```
    使用常见的命令行工具下载文件时，会收到`Content-Disposition`首部，因此如果需要保留原始文件名，可以用：
    ```
    wget --content-disposition http://{host}:{port}/file
    ```
    或者是：
    ```
    curl -OJ http://{host}:{port}/file
    ```
- 使用 curl 上传文件时，有 POST 和 PUT 两种方式，所以你可以用：
    ```
    curl -F file=@/path/to/file http://{host}:{port}
    ```
    或者是：
    ```
    curl -T /path/to/file http://{host}:{port}
    ```
