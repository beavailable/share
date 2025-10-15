# share
This is a command-line file sharing tool, which has just a single file and is easy to use.

## Features
- Crossing multiple platforms
- Sharing directories, files and texts
- Receiving files and texts
- Range request support
- Password sharing
- TLS support
- Zstd compression support (requires [python-zstandard](https://github.com/indygreg/python-zstandard), but is optional and not needed on Python 3.14+)
- QR code support (requires [python-qrcode](https://github.com/lincolnloop/python-qrcode), but is optional)

## Usage
```
usage: share.py [-b ADDRESS] [-p PORT] [-s] [-r] [-a] [-z] [-t] [-P [PASSWORD]] [-q] [-h]
                [--certfile CERTFILE] [--keyfile KEYFILE] [--keypass KEYPASS]
                [arguments ...]

positional arguments:
  arguments             a directory, files or texts

general options:
  -b, --bind ADDRESS    bind address [default: 0.0.0.0]
  -p, --port PORT       port [default: 8888]
  -s, --share           share mode (default mode)
  -r, --receive         receive mode, can be used with -s option (only for directory)
  -a, --all             show all files, including hidden ones, only for directory
  -z, --archive         share the directory itself as an archive, only for directory
  -t, --text            for text
  -P, --password [PASSWORD]
                        access password, if no PASSWORD is specified, the environment variable
                        SHARE_PASSWORD will be used
  -q, --qrcode          show the qrcode
  -h, --help            show this help message and exit

tls options:
  --certfile CERTFILE   cert file
  --keyfile KEYFILE     key file
  --keypass KEYPASS     key password
```

## Screenshot
![img](https://github.com/beavailable/share/blob/main/screenshot.gif)

## Tips
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
- To get an archive of a folder, you can add the `.tar.zst` extension to the url:
    ```bash
    http://{host}:{port}/any/folder.tar.zst
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
