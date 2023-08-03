FROM bams-aws.int.thomsonreuters.com:5001/tr-official/redhat
ENV http_proxy=webproxy.lon.corp.services:80
ENV https_proxy=webproxy.lon.corp.services:80
ENV no_proxy=.thomsonreuters.com
RUN yum install -y http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm
RUN yum update
RUN yum install -y python36u python36u-libs python36u-devel python36u-pip
RUN ln -s /usr/bin/python3.6 /usr/bin/python3
RUN ln -s /usr/bin/pip3.6 /usr/bin/pip3
RUN yum install -y swig
RUN yum groupinstall -y "Development Tools"
RUN pip3 install numpy
RUN pip3 install matplotlib
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install Pyro4
RUN pip3 install slackclient
RUN pip3 install requests
RUN mkdir /argos-adf
COPY start.sh /usr/bin/start.sh
RUN chmod 755 /usr/bin/start.sh
CMD tail -f /dev/null
