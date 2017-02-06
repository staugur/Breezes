FROM registry.saintic.com/python

MAINTAINER Mr.tao <staugur@saintic.com>

ADD src /Breezes

ADD misc/supervisord.conf /etc/supervisord.conf

ADD requirements.txt /tmp

WORKDIR /Breezes

RUN pip install --timeout 30 --index https://pypi.douban.com/simple/ -r /tmp/requirements.txt

EXPOSE 10210

ENTRYPOINT ["supervisord"]