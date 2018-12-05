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

* OpenCV based motion detection
* OpenCV based facial detection
* Email alerts upon face detection
* Email alerts upon motion detection
* Email alerts can be turned on/off
* Easy to setup JSON configuration file

### Getting started

1. Clone the repo into your home directory:
`sudo git clone https://github.com/Xaxis/rpysurveillance.git`

2. Update the following lines in `rpysurveillance.json` to match your sending email
addresses credentials and your target email address.

    ```python
    sender = 'source@gmail.com'
    gmail_password = 'yourpassword!'
    recipients = ['target@gmail.com']
    ```

There are further configuration values that can be changed. The non-obvious ones will
be better documented in the future.

3. Run the script:
`sudo python3 rpysurveillance.py`

### Author

Wil Neeley ( [twitter](http://twitter.com/wilneeley) / [linkedin](https://www.linkedin.com/in/wil-neeley-87500852/) )
