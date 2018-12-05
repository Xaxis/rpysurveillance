# rpysurveillance

## Summary

Python + OpenCV Surveillance System (tailored for Raspberry Pi)

This is a multi-camera surveillance system that performs motion and facial detection.

### Requirements

* A small computer such as a Raspberry Pi 3
* One or more USB cameras
* Python 3 installed
* OpenCV installed

### Features

* Easy to setup JSON configuration file
*

### Getting started

1. Clone the repo into your home directory:
`sudo git clone https://github.com/Xaxis/rpisurveillance.git`

2. Update the following lines in `motion_detected.py` to match your sending email
addresses credentials and your target email address.

    ```python
    sender = 'source@gmail.com'
    gmail_password = 'yourpassword!'
    recipients = ['target@gmail.com']
    ```

3. Run install the install script from within the `rpisurveillance` directory:
`cd rpisurveillance`
`chmod 777 install_rpi_surveillance.sh`
`sudo ./install_rpi_surveillance.sh`

4. That's all! Your motion detection system should work after your next reboot.
If you want to test your setup before rebooting you can run:
`sudo motion -s -c /home/.motion/motion.conf`

### Author

Wil Neeley ( [twitter](http://twitter.com/wilneeley) / [linkedin](https://www.linkedin.com/in/wil-neeley-87500852/) )
