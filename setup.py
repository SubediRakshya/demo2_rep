from setuptools import setup

package_name = 'dynamixel_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your@email.com',
    description='Dynamixel control using ROS2 service',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'motor_service = dynamixel_control.motor_service:main',
            'motor_client = dynamixel_control.motor_client:main',
        ],
    },
)
