from setuptools import setup

package_name = 'dynamixel_sdk_examples'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='Examples for controlling Dynamixel motors in ROS2',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'read_write_node = dynamixel_sdk_examples.read_write_node:main',
            'rotate_motor_node = dynamixel_sdk_examples.rotate_motor_node:main',
        ],
    },
)
