import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'amr_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='obayzakzak',
    maintainer_email='obayzakzak@todo.todo',
    description='Vision Perception Package for AMR Digital Twin',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'object_detector_node = amr_perception.object_detector_node:main',
        ],
    },
)
