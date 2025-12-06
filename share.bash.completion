_share() {
    local cur prev words cword commands
    _comp_initialize || return $?
    if [[ "$cur" == -* ]]; then
        COMPREPLY=($(compgen -W '-b --bind -p --port -s --share -r --receive -a --all -z --archive -t --text -P --password -A --auth-pattern -q --qrcode -h --help --certfile --keyfile --keypass' -- "$cur"))
    else
        case "$prev" in
            '-b')
                _comp_compgen_ip_addresses -a
                ;;
            '-p' | '--port' | '-A' | '--auth-path' | '--keypass') ;;
            *)
                if ! [[ -d "$prev" ]]; then
                    _comp_compgen_filedir
                fi
                ;;
        esac
    fi
}
complete -F _share share
