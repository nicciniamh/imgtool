#!/bin/bash
manmode=644
scriptmode=755
script=imgtool.py
manpage=imgtool.1
[ "$MANPATH" == "" ] && MANPATH=$(manpath)
trap died SIGUSR1
died() {
    exit 1
}
error() {
    echo "$*" >&2
}
die() {
    error "$*"
    kill -10 $$
}
getPath() {
    what="$1"
    where="$2"
    dest="$3"
    select foo in $(echo ${!where} | sed s/:/\ /g) Other Skip Quit; do  break; done
    case $foo in 
        Other )
            while true ; do
                read -p "Enter path for ${what}: " foo
                [ -d "$foo" ] && [ -w "$foo" ] && { echo "$foo"; return 0; }
                if [ ! -d  "$foo" ] ; then
                    read -p "$foo does not exist, Create? " -n 1 -r
                    echo
                    if [[ $REPLY =~ ^[Yy]$ ]] ; then
                        if mkdir -p "$foo" ; then
                            eval $dest="$foo"
                            return 0
                        else
                            error "Cannot create path for ${what}"
                            return 1 
                        fi
                    else
                        return 1
                    fi
                fi
            done
            ;;
        Quit )
            return 2
            ;;
        Skip )
            return 1
            ;;
        * )
            eval $dest="$foo"
            return 0
            ;;
    esac
}
cat << EOF
This script is a simple installer for imgtool.
EOF
echo "Please select destination for the program script"
getPath "Program Script" PATH scriptPath
rc=$?
(( rc > 0 )) && die "Install Terminated."
echo "Please select destination for the program manual page"
getPath "Manual Page" MANPATH manPath
rc=$?
(( rc == 2 )) && die "Install Terminated."
#echo "Install program to [$scriptPath]"
echo install -pbm ${scriptmode} $script ${scriptPath}/${script%.*}
install -pbm ${scriptmode} $script ${scriptPath}/${script%.*}
(( rc == 0 )) || exit
#echo "Install Manual Page to [$manPath]"
echo install -pbm ${manmode} $script ${manPath}/man1/$manpage
install -pbm ${manmode} $manpage ${manPath}/man1/$manpage
