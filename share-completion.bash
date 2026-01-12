_share() {
    local cur prev words cword commands
    _comp_initialize || return $?
    if [[ "$cur" == -* ]]; then
        COMPREPLY=($(compgen -W '-b --bind -p --port -s --share -r --receive -a --all -z --archive -t --text -P --password -R --auth-rule -q --qrcode -h --help --certfile --keyfile --keypass' -- "$cur"))
    else
        case "$prev" in
            '-b')
                _comp_compgen_ip_addresses -a
                ;;
            '-p' | '--port' | '-R' | '--auth-rule' | '--keypass') ;;
            *)
                if ! [[ -d "$prev" ]]; then
                    _comp_compgen_filedir
                fi
                ;;
        esac
    fi
}
complete -F _share share
