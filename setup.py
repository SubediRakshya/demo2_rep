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
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='Dynamixel motor control with ROS2 service-client structure',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'motor_service = dynamixel_control.motor_service:main',
            'motor_client = dynamixel_control.motor_client:main',
        ],
    },
)
