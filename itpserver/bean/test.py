# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-06-13 10:58:22
File Name: test.py @v1.0
"""
import os
import sys
import time
import smtplib
import unittest
import pynliner
from email.mime.text import MIMEText
from email.header import Header

import HTMLTestRunner

from tests.tests_wen.test_api import APITestCase
# from tests.case_api import deve_URL, test_URL, broker_url_deve, broker_url_test


# Test case path.
case_path = os.path.join(os.getcwd())
# Report path.
report_path = os.path.join(os.getcwd(), 'report')


def all_case():
    loader = unittest.TestLoader()
    ln = lambda f: getattr(APITestCase, f).im_func.func_code.co_firstlineno
    lncmp = lambda a, b: cmp(ln(a), ln(b))
    loader.sortTestMethodsUsing = lncmp

    # discover = unittest.defaultTestLoader.discover(case_path, pattern="test*.py", top_level_dir=None)
    suite = unittest.TestSuite()
    # suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMathFunc))
    suite.addTests(loader.loadTestsFromTestCase(APITestCase))

    return suite


def sendReport(file_new):
    with open(file_new, 'rb') as f:
        mail_body = f.read()

    msg = MIMEText(mail_body, 'html', 'utf-8')
    msg['Subject'] = Header('ITPServer自动化测试报告', 'utf-8')
    msg['From'] = 'ci-build@skyguardmis.com'
    msg['To'] = 'lianpengcheng@skyguardmis.com;jiatian@skyguardmis.com'

    smtp = smtplib.SMTP('mail.skyguardmis.com')
    smtp.set_debuglevel(1)
    smtp.login('ci-build@skyguardmis.com', '')
    smtp.sendmail(msg['From'], msg['To'].split(';'), msg.as_string())

    smtp.quit()
    print('test report has send out!')


def newReport(testReport):
    lists = os.listdir(testReport)
    lists2 = sorted(lists)
    file_new = os.path.join(testReport, lists2[-1])
    return file_new


def inlineStyle(file):
    with open(file, 'rb') as f:
        body = f.read()
    output = pynliner.fromString(body)
    inline_file = open('report/inline_file', 'w')
    inline_file.write(output)
    inline_file.close()


if __name__ == '__main__':
    os.system('nohup python manage.py runserver 0.0.0.0:8080 &')
    time.sleep(5)
    # loader = unittest.TestLoader()
    # ln = lambda f: getattr(APITestCase, f).im_func.func_code.co_firstlineno
    # lncmp = lambda a, b: cmp(ln(a), ln(b))
    # loader.sortTestMethodsUsing = lncmp

    # unittest.main(testLoader=loader, verbosity=2)
    report_abspath = os.path.join(report_path, "ITPServer测试报告_EN.html")

    # Write result to file.
    fp = open(report_abspath, "wb")
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title=u'ITPServer自动化测试报告_EN', description=u'用例执行情况：')
    # Use add_case get res.
    runner.run(all_case())
    status = runner.status

    fp.close()

    # Get latest report
    # new_report = newReport(report_path)
    inlineStyle(report_abspath)

    # Send report
    sys.exit('Error' in ''.join(status) or 'Failure' in ''.join(status))
