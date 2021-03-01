FROM reg-cloud.skyguardmis.com/elastic/logstash:6.7.2

ADD ls-7.0.1-jrjackson-fix-1.tar.gz /usr/share/logstash

USER root
RUN chown -R logstash:logstash /usr/share/logstash

USER logstash
WORKDIR /opt/logstash

