#!/bin/bash

## This script has been verified with `shellcheck`
##
## - Create a symbolic link to this script file, e.g.;
##   ```
##   sudo ln -s /home/user/scripts/flask_music_search/music-search.sh /home/user/scripts/music-search
##   ```

# me="${0##*/}"
# echo "$me called"
# echo
# echo "# received arguments ------->  ${@}     "
# echo "# \$1 ----------------------->  $1       "
# echo "# \$2 ----------------------->  $2       "
# echo "# \$3 ----------------------->  $3       "
# echo "# \$4 ----------------------->  $4       "
# echo "# path to me --------------->  ${0}     "
# echo "# parent path -------------->  ${0%/*}  "
# echo "# my name ------------------>  ${0##*/} "
# echo

## Set paths as appropriate to your system:

run_dir="$HOME/scripts/flask_music_search/"
activate_path="$run_dir/.venv/bin/activate"

# echo "activation path: $activate_path"

Usage() {
    echo "This script runs a flask app on a WSG server (gunicorn). The app implements a search utility for a local "
    echo "music Postgre DB."
    echo "Usage:"
    echo "    -i IP address of the machine on which to run the gunicorn server                          "
    echo "    -p port on the machine the gunicorn server is to use                                      "
    echo "    --help"
}

while [[ $# -gt 0 ]];
do
    case "$1" in
        -i|--ip)
            ip="$2"
            shift
            ;;
        -p|--port)
            port="$2"
            shift
            ;;
        --help|*)
            Usage
            exit 1
            ;;
    esac
    shift
done

if [ -z "$ip" ]; then
    # ip=$(hostname -i | sed -r 's/^[0-9\.]+\ +//g')
    ip="127.0.0.1"
fi

if [ -z "$port" ]; then
    port="5000"
fi

# Mount music share in fstab (edit /etc/fstab to add the line below):
# //192.168.1.24/Multimedia/music/        /home/pi/lanmount/music cifs    username=admin,password=$ognuM,uid=1000,gid=1000        0 0

# start tailnet books and tailnet music search in crontab ($ crontab -e and add
# these lines):
# @reboot /home/pi/scripts/start-tailnet-books.sh
# @reboot /home/pi/scripts/start-tailnet-music-search.sh

. "$activate_path" && cd "$run_dir" && gunicorn --workers 4 --timeout 240 --bind "$ip":"$port" app:app  && deactivate

