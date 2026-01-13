from setuptools import setup, find_packages


setup(name='zoypack',
      version='1.0.2',
      author='ZoyLuo',
      author_email='zoyluofakeall@163.com',
      description='My own package',
      long_description='For detail please visit https://github.com/zoyluoblue/zoypack',
      long_description_content_type="text/markdown",
      maintainer='ZoyLuo',
      maintainer_email='zoyluofakeall@163.com',
      packages=find_packages(),
      package_data={'': ['*.so']},
      platforms=["all"],
      url='https://github.com/zoyluoblue/zoypack',
      install_requires=[
          'concurrent_log_handler',
          'pymongo',
      ],
      # extras_require={
      #     'sql': ["pymysql"],
      # },
      )
