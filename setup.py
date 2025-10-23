from setuptools import setup
import os
from glob import glob

package_name = 'dynamixel_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include .srv files
        (os.path.join('share', package_name, 'srv'), glob('srv/*.srv')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your@email.com',
    description='Control Dynamixel motors using client-server communication in ROS 2.',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'rotate_motor_client = dynamixel_control.rotate_motor_client:main',
            'rotate_motor_service = dynamixel_control.rotate_motor_service:main',
        ],
    },
)
