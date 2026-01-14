#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root"
    exit 1
fi


USERPWD=`head -c 100 /dev/urandom | tr -dc 'a-z0-9' | fold -w 8 | head -c 8`

echo "wass:$USERPWD" | chpasswd
echo "User wass, password: " $USERPWD
nohup /usr/sbin/sshd -D &

