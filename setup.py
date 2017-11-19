from distutils.core import setup

setup(
    name='sms-demo',
    version='0.9.1',
    packages=['smsdemo', 'smsdemo.httpserver', 'smsdemo.flaskserver',
              'smsdemo.aiohttpserver'],
    url='',
    license='MIT',
    author='Alex Lee; Michael McVady; X.D. Zhai',
    author_email='support@telnyx.com',
    description='Sample implementations of SMS echo server using Telnyx SMS API'
)
