#!/bin/bash


echo "Build CPU or GPU version?"
echo "Please be sure that nvidia-docker2 is installed if you choose the GPU version"

select yn in "GPU" "CPU"; do
    case $yn in
        GPU ) docker build -f Dockerfile.gpu  --build-arg USER_ID=$(id -u ${USER}) --build-arg GROUP_ID=$(id -g ${USER}) -t wassfast:gpu .; exit;;
        CPU ) docker build -f Dockerfile --build-arg USER_ID=$(id -u ${USER}) --build-arg GROUP_ID=$(id -g ${USER}) -t wassfast:cpu .; exit;;
    esac
done


#docker build  --build-arg USER_ID=$(id -u ${USER}) --build-arg GROUP_ID=$(id -g ${USER}) -t wassfast:dev .
#docker build -f Dockerfile.gpu  --build-arg USER_ID=$(id -u ${USER}) --build-arg GROUP_ID=$(id -g ${USER}) -t wassfast:gpu .
