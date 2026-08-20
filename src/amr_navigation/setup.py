import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'amr_navigation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='obayzakzak',
    maintainer_email='obayzakzak@todo.todo',
    description='SLAM and Navigation package for AMR Digital Twin',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'navigation_benchmarker = amr_navigation.navigation_benchmarker:main',
        ],
    },
)
