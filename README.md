# Newt (MicroSD Card Duplicator)
Newt clones multiple MicroSD cards from one .img file.

**Table of contents:**

<!-- toc -->

- [Required Operating System](#required-operating-system)
- [Required Hardware](#required-hardware)
- [Project](#project)
- [Installation](#installation)
- [Get an image](#get-an-image)
- [Using newt](#using-newt)
- [Original Authors](#original-authors)
- [Software Overview](#software-overview)
- [References](#references)
- [Versioning](#versioning)
- [License](#license)

<!-- tocstop -->

## Required Operating System
Latest version of Raspberry Pi OS

## Required Hardware
* 8GB Raspberry Pi 4 with Case connected to Power Adapter
* 64GB Class 10, Ultra MicroSD Card with Raspberry Pi OS inserted into the Raspberry Pi's MicroSD Card slot
* Powered USB 3.0 hub (10 ports) with power cord and USB cable connected to Raspberry Pi
* MicroSD card USB 3.0 readers (10 total) inserted into USB Hub
* 1-10 16GB or 32GB Class 10, Ultra MicroSD cards inserted into USB readers

## Project
* [Detailed project instructions])https://sites.google.com/site/cartwrightraspberrypiprojects/microsd-card-duplicator)

## Installation 
Newt runs headless on a Raspberry Pi 4 using Raspberry Pi OS on a home LAN.

These directions assume a [Raspberry Pi is properly setup](https://sites.google.com/site/cartwrightraspberrypiprojects/home/steps/setup-raspberry-pi-3-with-raspbian) and running Raspberry Pi OS and the goal is to run the MicroSD Card duplicator as a networked device on a home LAN.

Be sure to replace items enclosed by <sub><sup>♣</sup></sub>s with your value 

install.sh installs all the required software, makes any needed directories and sets any needed permissions. install.sh is a generic installer and relies on install.cfg to set up newt correctly.

* Step 1. Open a terminal window
* Step 2. From the terminal window, ssh into a Raspberry Pi 4 running Raspberry PI OS. 
```
ssh pi@newt.♣your-hostname♣
password: ♣your-password♣
```
* Step 3. On the RPi, Ddwnload and run newt's install.sh script and configuration file 
```
wget https://raw.githubusercontent.com/dumbo25/newt/master/install.sh
wget https://raw.githubusercontent.com/dumbo25/newt/master/install.cfg
sudo bash install.sh
```
* Step 4. On the RPi, run the following commands to add a line to the end of apache2.conf. Restart the service and check that it is correct. Debian-based dists like Raspberry Pi OS use apache2.conf, other linux dists use httpd.conf. 
```
hostname -I
♣your-ip-address♣
echo "ServerName ♣your-ip-address♣" | sudo tee -a /etc/apache2/apache2.conf
sudo systemctl restart apache2.service
sudo systemctl status apache2.service -l --no-pager
```
* Step 5. On lthe RPi, do the following:
```
cd ~/.
django-admin startproject newt_site
sudo python3 manage.py migrate
```
then either this
```
cd /home/pi/newt_site
sudo python3 manage.py runserver
```
or this
```
cd /home/pi/newt
sudo python3 server.py cmd
```
* Step 6. Open a browser and enter 
```
http://♣your-hostname♣.local
```

## django.sh
django.sh setups a project directory, a virtual env and django on a raspberry running headless. So, the website is visible from a laptop on the same LAN. django.cfg contains the configuration for the script.

## Get an image
Newt requires at least one image. 

* Download image from here to your laptop https://www.raspberrypi.com/software/operating-systems/
* Open a terminal window on laptop
* Change directory to Downloads
```
cd Downloads
```
* Copy the file from MacBook to Raspberry Pi
```
scp 2021-05-07-raspios-buster-armhf-lite.zip pi@newt:/home/pi
```
* Open a terminal window. ssh to Raspberry Pi. unzip the image zip file. Copy file to clone directory
```
ssh pi@♣your-hostname♣
password: ♣your-password♣
unzip scp 2021-05-07-raspios-buster-armhf-lite.zip 
cp 2021-05-07-raspios-buster-armhf-lite.img newt/clone/.
```

## Using newt
A Raspberry Pi (RPi) runs the newt webserver. A user opens a browser and connects to the RPi's webserver 
```
http://♣your-hostname♣ 
```
Newt clones one image to 1-10 MicroSD cards. I believe the number of MicroSD Cards can be increased by adding more USB Hubs, but I have not tested this.


### Accepted image file
Newt will accept any image file ending with .img name. Other extensions will silently be ignored.

### Auto discovery of available readers
When refreshing the newt web page (or accessing it), newt will scan for available readers, and after some seconds, will show them on the menu. A sum of all readers is also shown.


## Original Authors
* [aaronnguyen/OSID](https://github.com/aaronnguyen/osid-python3) - python3 version of OSID Project
* [rockandscissor/OSID](https://github.com/rockandscissor/osid) - Base OSID Project originally written in PHP and Bash

## Software Overview
* Django is a web framework that needs a webserver to operate. 
* Unlike most lightweight webservers, Apache2 is a secure webserver. 
* Most webservers cannot communicate with python applications. So, WSGI or ASGI is needed to communicate between python applications and the web server.
  * WSGI only allows synchronous communication

### Significant Changes from OSID version
* added generic install.sh with duplicator specific install.cfg
* simplify directions
* migrate from CherryPy to Django
  * Statistics: Django: ★s 60.086, Flask: ★s 56,845, CherryPy: ★s 1,458; source PyPi 10OCT2021
  * If I get stuck on some aspectof using a framework, then I want a lot of resources. So, the more people using, then the more likely I am to find the ssolution to the problem I am facing
* migrate from skeleton to uikit
  * Statistics: [skeleton](https://github.com/dhg/Skeleton): ★s 18.4k, [uikit](https://github.com/uikit/uikit) ★s 17.1k [pure](https://github.com/pure-css/pure/)★s 21.9k; source GitHub 10OCT2021
  * Using an obfuscated skeleton is not really an oiption; migration or update is required
  * I want a minimal css that is upto date, responsive and easy to use. As an dded benefit, uikit is also used to develop iPhone apps
* To Dos:
  * getImages doesn't show anything in the browser. Images are in the directory
  * also no devices are showing
  * font of credits is too large
  * get mylog to write to same directory (not newt/server, but newt/log) or at best same file as server.py (access.log)
  * add an image of what the app looks like to this readme.md

### Dependencies
* [Django](https://www.djangoproject.com/) - django web framework
  * [Deploy Django](https://docs.djangoproject.com/en/3.2/howto/deployment/)
* [apache2](https://httpd.apache.org/) - webserver
* [uikit](https://github.com/uikit/uikit) - css 
* [Raspberry Pi OS](https://www.raspberrypi.org/) - Raspberry Pi Operating system
* [sqlite3](https://www.sqlite.org/index.html) - lightweight SQL database
* [mod_wsgi](https://pypi.org/project/mod-wsgi/) - wsgi 
  * Not used: ASGI allows asynchronous communication (daphne, uvicorn, hypercorn)
* Things to remove:
  * [CherryPy](http://docs.cherrypy.org/en/latest/) - API Library for Python used to manage all actions
  * [Skeleton-Framework](https://github.com/skeleton-framework/skeleton-framework) - CSS framework used to structure Web UI
  * dcfldd ???

## References
* [nettings/tarot](https://github.com/nettings/tarot) - very cool improvements, changed from python to php and js
* [Raspberry Tips](https://raspberrytips.com/create-image-sd-card/) How to Create an Image of a Raspberry Pi SD Card?
* [RaspberryPi.org](https://www.raspberrypi.org/documentation/computers/getting-started.html#using-raspberry-pi-imager) Using Raspberry Pi Imager
* [RaspberryPi/github](https://github.com/raspberrypi/rpi-imager) Github repository for Raspberry Pi Imager
* [billw2/rpi-clone](https://github.com/billw2/rpi-clone) RPi clone
* [Igoro Oseledko](https://www.igoroseledko.com/backup-options-for-raspberry-pi/) Backup Options for Raspberry Pi
* [tyrower/diy-duplicator](https://github.com/tyrower/diy-duplicator) Micro SD duplicator using mdadm (RAID disk utilities) written in bash
* [PiMyLifeUp/Emmet](https://pimylifeup.com/raspberry-pi-django/) Installing Django on your Raspberry Pi
* [Django Install](https://docs.djangoproject.com/en/3.2/topics/install/) How to install Django
* [Django wsgi](https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/modwsgi/) How to use Django with Apache and mod_wsgi
* [Django Application](https://docs.djangoproject.com/en/3.2/intro/tutorial01/) Writing your first Django app

## Versioning
[SemVer](http://semver.org/) is used for version numbers. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

Version needs to be changed in index.html, monitor.html.

## License
This project is licensed under the GNU GPLv3 - see the [LICENSE.md](LICENSE.md) file for details
