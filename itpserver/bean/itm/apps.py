# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-04-12 10:46:12
File Name: apps.py @v2.0
"""
from __future__ import unicode_literals

from django.apps import AppConfig


class ItmConfig(AppConfig):

    name = 'itm'

    def ready(self):
        """
        Init some opts when app is ready.
        Print log into uwsgi log instead of app logger.
        """
        # self.init_es_templete()
        self.init_uwsgi_log()

    def init_uwsgi_log(self):
        import os
        from crontab import CronTab

        cron = CronTab(user=True)
        comment = 'uwsgilogrotat'
        res = list(cron.find_comment(comment))

        if not res:
            is_dev = os.environ.get('ITM_CONFIG')

            if is_dev == 'test':
                job = cron.new(command='sh /home/share/itpserver/bean/logbackups.sh')
            else:
                job = cron.new(command='sh /opt/skyguard/itpserver/logbackups.sh')

            job.setall('0 0 * * *')
            job.set_comment(comment)
            cron.write()
            print('Uwsgi log rotat init success!')

        elif len(res) == 1:
            print('Uwsgi log rotat has init!')

        else:
            print('Uwsgi log rotat has error!')

    def init_es_templete(self):
        from config import config
        from elasticsearchorm import ElasticSearchClient

        _es = ElasticSearchClient.get_es_servers()

        try:
            if not _es.indices.exists_template(name='es'):
                _es.indices.put_template(name='es', body=config.es_templete)
                print('ES templete init success!')
            else:
                print('ES templete has init!')

        except:
            import traceback
            traceback.print_exc()
            print('ERROR: ES templete init failed!')
