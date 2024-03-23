# share
This is a command-line file sharing tool, which has just a single file and is easy to use.

# Features
- Crossing multiple platforms
- Sharing directories, files and texts
- Receiving files and texts
- Range request support
- Password sharing
- TLS support

# Usage
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

# Screenshot
![img](https://github.com/beavailable/share/blob/main/screenshot.gif)

# Tips
- If you're sharing just one file, you can use the shortcut name `file` to access it：
    ```bash
    http://{host}:{port}/file
    ```
    To save with the original filename with `wget`:
    ```bash
    wget --content-disposition http://{host}:{port}/file
    ```
    Or with `curl`:
    ```bash
    curl -OJ http://{host}:{port}/file
    ```
- To download a folder with `curl`, just add `.zip` to the url:
    ```bash
    curl -O http://{host}:{port}/any/folder.zip
    ```
- If you want to upload files to the sharing server with `curl`, you can use:
    ```bash
    curl -F file=@/path/to/file http://{host}:{port}
    # create new folders at the same time
    curl -F file=@/path/to/file http://{host}:{port}/custom/path
    ```
    Or:
    ```bash
    curl -T /path/to/file http://{host}:{port}
    # create new folders at the same time
    curl -T /path/to/file http://{host}:{port}/custom/path/
    # with a different filename
    curl -T /path/to/file http://{host}:{port}/custom/path/custom-filename
    ```
