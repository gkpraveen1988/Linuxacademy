FROM alpine
LABEL maintainer "arush[dot]sal[at]gmail"
LABEL Description="This image is used to start the linuxacademy-dl executable." Version="1.0"
LABEL Usage='docker run arush/linuxacademy-dl:latest -v <local-directory>:/media'
VOLUME ["/media"]
RUN ["apk", "add", "--no-cache", "python2", "ffmpeg", "py-pip", "ca-certificates"]
COPY [".","/opt/linuxacademy-dl"]
WORKDIR /opt/linuxacademy-dl
RUN ["python2", "setup.py", "install"]
WORKDIR /media
ENTRYPOINT ["/bin/sh", "-i"]
