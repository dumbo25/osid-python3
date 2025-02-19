#! /usr/bin/env python3
"""
This script runs a web server for cloning multiple MicroSD Cards.

A Raspberry Pi 4 connects to USB 3.0 powered hub

Modules or Tools that must be installed for script to work:
    Run install.sh

References:
    Original Author: Vadim Kantorov
    Original Source: https://github.com/vadimkantorov/wemosetup

My Guidelines for pythonic code:
    https://sites.google.com/site/cartwrightraspberrypiprojects/home/footer/pythonic
"""

############################# <- 80 Characters -> ##############################
#
# This style of commenting is called a garden bed and it is frowned upon by
# those who know python. But, I like it. I use a garden bed at the top to track
# my to do list as I work on the code, and then mark the completed To Dos.
#
# Within the code, To Dos include a comment with ???, which makes it easy for
# me to find
#
# Once the To Do list is more-or-less complete, I move the completed items into
# comments, docstrings or help within the code. Next, I remove the completed
# items.
#
# To Do List:
#   a) Migrate from Raspberry Pi 2 to Raspberry Pi 4
#   b) Eliminate need for a Raspberry Pi Touch Display
#   c) Create install.sh to download files from github repository (for people who just want to use code as is)
#   d) migrate from raspbian to Raspberry Pi OS
#   e) if possible use one USB on RPi as source and 7 USBs on HUB as destination (I don't want the image on the RPi)
#   f) might need to get missing graphics from other repos???
#   g) figure out how to get to website:
#      g.1) python3 system/server.py, what is URL?
#      g.2) Allow port 80 in ufw (allowed);
#      g.3) do www files need to be moved to /var/www ???
#      g.4) do I have to have some microsd cards inserted? there are no .img files
#   h) Add argparse
#   i) Add docstrings
#   j) Expand help
#   k) Better messaging
#   l) migrate from cherrypy to flask or to a python-only implementation:
#      https://pythonbasics.org/webserver/
#      https://discourse.world/h/2019/10/18/5-Ways-to-Make-a-Python-Server-on-a-Raspberry-Pi-Part-1
#      redmoon: https://github.com/dumbo25/flaskMenu
#   m) need a systemd service to keep the server running
#   p) figure out how it works using USBs on raspberry pi; create fake *.img file; or  get RPiOS lite
#   q) need to configure apache2 config file and then reload apache2
#       echo "ServerName 127.0.0.1" | sudo tee -a /etc/apache2/apache2.conf
#       sudo systemctl reload apache2.service
#
#   x) run pydoc
#   y) run pylint
#   z) upload final code to github
#
# Do later or not at all:
#
# Won't Do:
#
# Completed:
#   - Added mylog
#
############################# <- 80 Characters -> ##############################

# Built-in Python3 Modules
import json
import os
import sys
import subprocess
import configparser
import socket

# Modules that must be installed (pip3)
import cherrypy

# My Modules (from github)
# pylint reports; C0413: Import "from mylog import MyLog" should be placed at
# the top of the module. However, I am not sure how to fix this issue.
# sys.path.append is required for me to import my module
sys.path.append("..")
from mylog import MyLog

# ??? old to do: too many config_parse blocks, create a function to easily call it

# Global Variables
HostIP = "127.0.0.1"

# class SDCardDupe(object):
class SDCardDupe(object):
    @cherrypy.expose
    def index(self):
        global logger
        global HostIP

        logger.logPrint("INFO", "index")
        # get host configs from server.ini
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )

        # Get webpage, then replace needed parts here
        www_path = config_parse['DuplicatorSettings']['HtmlPath']
        html_string = open(www_path + 'index.html', 'r').read()
        # hostname_port = config_parse['DuplicatorSettings']['Host']+":"+config_parse['DuplicatorSettings']['SocketPort']
        hostname_port = HostIP+":"+config_parse['DuplicatorSettings']['SocketPort']
        html_string = html_string.replace("replacewithhostnamehere",hostname_port)

        css_string = '<style>' + open(config_parse['DuplicatorSettings']['SkeletonLocation'], 'r').read() + '</style>'
        html_string = html_string.replace("<style></style>",css_string)

        return html_string


    @cherrypy.expose
    def monitor(self):
        global logger
        global HostIP

        logger.logPrint("INFO", "monitor")

        # get host configs from server.ini
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )

        # Get webpage, then replace needed parts here
        www_path = config_parse['DuplicatorSettings']['HtmlPath']
        html_string = open(www_path + 'monitor.html', 'r').read()
        # hostname_port = config_parse['DuplicatorSettings']['Host']+":"+config_parse['DuplicatorSettings']['SocketPort']
        hostname_port = HostIP+":"+config_parse['DuplicatorSettings']['SocketPort']
        html_string = html_string.replace("replacewithhostnamehere",hostname_port)

        css_string = '<style>' + open(config_parse['DuplicatorSettings']['SkeletonLocation'], 'r').read() + '</style>'
        html_string = html_string.replace("<style></style>",css_string)

        return html_string

    @cherrypy.expose
    def posted(self,img_file,devices):
        global logger
        global HostIP

        logger.logPrint("INFO", "posted")

        # get all mounted items on the rpi
        mounted_list = []
        mounted_volumes_output = subprocess.check_output("mount", shell=True)
        for mount_line in str(mounted_volumes_output.decode("utf-8")).split("\n"):
            device_name = mount_line.split(" on ",1)[0]
            if device_name not in mounted_list:
                mounted_list.append(device_name)

        # If one device has been posted, a string is passed into function
        # Need to convert to a list
        if type(devices) is str:
            devices = [devices]

        # nested for loop, maybe we can optimize this later
        for dev_path in devices:

            reduced_list = []
            for mounted_item in mounted_list:
                # assumptions made, there will be no collisions, dont have to pop element
                # but to reduce the cost of loop, will pop element by creating new list
                if dev_path in mounted_item:
                    umount_disk_cmd = "sudo umount %s"%mounted_item
                    subprocess.call(umount_disk_cmd.split(" "))
                else:
                    reduced_list.append(mounted_item)

            mounted_list = []
            mounted_list.extend(reduced_list)


        # get host configs from server.ini
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )

        if not os.path.exists(config_parse['DuplicatorSettings']['Logs']):
            os.makedirs(config_parse['DuplicatorSettings']['Logs'])

        #Save current img name to logs
        with open(config_parse['DuplicatorSettings']['Logs'] + "/imagename.info", 'w') as out:
            out.write(os.path.basename(img_file))
        out.close()

        # Run dd command and output status into the progress.info file
        dd_cmd = "sudo dcfldd bs=4M if=" + img_file
        dd_cmd += " of=" + " of=".join(devices)
        dd_cmd += " sizeprobe=if statusinterval=1 2>&1 | sudo tee "
        dd_cmd += config_parse['DuplicatorSettings']['Logs'] + "/progress.info"
        dd_cmd += " && echo \"osid_completed_task\" | sudo tee -a "
        dd_cmd += config_parse['DuplicatorSettings']['Logs'] + "/progress.info"

        # Planned to run this in localhost only.
        # But if there are plans to put this on the network, this is a security issue
        # Just a workaround to get it running by subprocess
        dd_cmd_file = config_parse['DuplicatorSettings']['Logs']+"/run.sh"
        with open(dd_cmd_file,'w') as write_file:
            write_file.write(dd_cmd)

        subprocess.Popen(['sudo', 'bash', dd_cmd_file], close_fds=True)

        # hostname_port = config_parse['DuplicatorSettings']['Host']+":"+config_parse['DuplicatorSettings']['SocketPort']
        hostname_port = HostIP+":"+config_parse['DuplicatorSettings']['SocketPort']
        monitor_url = "http://" +  hostname_port + "/monitor";

        html_string = "<html><head>"
        html_string += "<meta http-equiv=\"refresh\" content=\"0; URL='" +monitor_url+ "'\" />"
        html_string += "</head></html>"

        return html_string



    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getStatus(self):
        global logger
        global HostIP

        logger.logPrint("INFO", "getStatus")

        # get host configs from server.ini
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )
        progress_file = config_parse['DuplicatorSettings']['Logs'] + "/progress.info"

        # pull data from imagename.info for image name
        with open(config_parse['DuplicatorSettings']['Logs'] + "/imagename.info", 'r') as out:
            imgname = out.read()
        out.close()

        # pull data from progress.info file and feed back to call
        cat_cmd = "sudo cat "+ progress_file
        cat_output = str(subprocess.check_output(cat_cmd, shell=True).decode("utf-8"))
        if "records in" in cat_output and "records out" in cat_output and "osid_completed_task" in cat_output:
            percentage = "100%"
            time_remains = "00:00:00"

        elif "%" in cat_output:
            current_line = cat_output.split("[")[-1]
            percentage = current_line.split(" of ")[0]
            time_remains = current_line.split("written. ")[1].split(" remaining.")[0]

        # send the data as a json
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps({'percentage':percentage.replace('%',''),'time_remaining':time_remains,'img_name':imgname})


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getDevices(self):
        global logger
        global HostIP

        logger.logPrint("INFO", "getDevices")

        list_devices = []

        # Refresh partition to discover all available medias
        refresh_disk_cmd = "sudo /sbin/partprobe"
        subprocess.check_output(refresh_disk_cmd, shell=True)

        # command to get a list of devices on OS
        get_disk_cmd = "lsblk -d | awk -F: '{print $1}' | awk '{print $1}'"
        cmd_device_list_output = subprocess.check_output(get_disk_cmd, shell=True)

        # break down the list to only usb devices
        for device_name in str(cmd_device_list_output.decode("utf-8")).split("\n"):
            if len(device_name) > 0 and 'NAME' not in device_name and 'mmcblk0' not in device_name:

                # get the block size of the device and the gb size
                get_disksize_cmd = "cat /sys/block/" + device_name + "/size"
                cmd_blocksize_output = subprocess.check_output(get_disksize_cmd, shell=True).decode("utf-8").rstrip("\n")
                device_size_gb = str(round(((int(cmd_blocksize_output) / 2) / 1024) / 1024, 2)) + 'G';
                # list_devices[device_name] = str(device_size_gb) + 'G'
                list_devices.append({'name': "/dev/"+device_name, 'size': device_size_gb})

        # send the data as a json
        cherrypy.response.headers['Content-Type'] = 'application/json'
        # return json.dumps(dict(Devices=list_devices))
        return json.dumps(list_devices)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getImages(self):
        global logger
        global HostIP

        logger.logPrint("INFO", "getImages")

        list_images = []

        # get the path of images from the ini file
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )

        # get the list of images and check if valid img file
        for img_file in os.listdir(config_parse['DuplicatorSettings']['ImagePath']):
            img_fullpath = os.path.join(config_parse['DuplicatorSettings']['ImagePath'], img_file)
            if os.path.isfile(img_fullpath) and  os.path.splitext(img_file)[1] == '.img':

                # get the size of the image
                img_filesize_cmd = "ls -sh " + img_fullpath
                img_size_cmd_output = subprocess.check_output(img_filesize_cmd, shell=True).decode("utf-8").rstrip("\n")

                # output is "Size Filename"
                # img_size_gb = round(((int(img_size_cmd_output.split(' ')[0]) / 2) / 1024) / 1024, 2);
                img_size_gb = img_size_cmd_output.split(' ')[0]

                # prep the data to send
                list_images.append({'filename': img_file, 'fullpath': img_fullpath, 'filesize': img_size_gb})

        # send the data as a json
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(list_images)

def main(logger):
    global HostIP

    # Original script failed, with -h or --help or no options
    # Optional arguments, like -h or --help don't work where options have Required = True set
    # help text should be limited to 80characters
    if ("--help" in sys.argv) or ("--h" in sys.argv) or ("-h" in sys.argv) or (len(sys.argv) == 1):
        logger.logPrint("INFO", '''
\033[1mNAME\033[0m
     duplicator -- duplicator is utility for cloning MicroSD cards used in
         Raspberry Pis and other devices. The tool takes one image and copies
         it to 7 other MicroSD cards.

\033[1mSYNOPSIS\033[0m
     sudo python3 server.py [commands] [-options]

\033[1mDESCRIPTION\033[0m
     Duplicator adds a networked based GUI to disk copying utilities.

     The following WeMo commands are available. All options listed for a
     command are required:

??? commands need to be defined
         add --ip <ip> --port <p>
             Add a device to a WeMo bridge

         bridge
             List the friendly name, IP address and port of all WeMo devices on
             a WeMo Bridge or home network

     The options are defined as:
??? options need to be defined
       --ip <ip>           IP Address of device

       --name              Friendly name of WEMO

       --password <pswd>   Password for home Wi-Fi
''')
    else:
        # ??? add argparse
        #   ??? log.screen and tools.session.on should be options set from command line
        #   ??? logger level and output should be command line options
        # ??? cherrypi is writing to a log file - ???

        # gert host IP Address, ignore the IP address in server.ini
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        HostIP = s.getsockname()[0]

        # get host configs from server.ini
        # note: is there a way to put the config into conf and pull from api functions - ??? not sure what this means ???
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )

        conf = {
            'global':{
                # 'server.socket_host': config_parse['DuplicatorSettings']['Host'],
                'server.socket_host': HostIP,
                'server.socket_port': int(config_parse['DuplicatorSettings']['SocketPort']),
                'log.access_file' : config_parse['DuplicatorSettings']['Logs']+"/access.log",
                'log.screen': True,
                'tools.sessions.on': True
            }
        }

        print("DEBUG: conf:")
        print(conf)

        print("DEBUG: grabbed lines from ~105")
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )
        www_path = config_parse['DuplicatorSettings']['HtmlPath']
        print("DEBUG: index: www_path = " + www_path)
        print("End of DEBUG: grabbed lines from ~105")

        # Get webpage, then replace needed parts here
        hostname_port = config_parse['DuplicatorSettings']['Host']+":"+config_parse['DuplicatorSettings']['SocketPort']
        print("DEBUG: hostname_port = " + hostname_port)
        print("DEBUG: HostIP = " + HostIP)

        # create a daemon for cherrpy so it will create a thread when started
        cherrypy.process.plugins.Daemonizer(cherrypy.engine).subscribe()

        cherrypy.quickstart(SDCardDupe(), '/', conf)

if __name__ == '__main__':
    logger = MyLog()
    logger.setLevel("INFO")
    logger.setOutput("CONSOLE")
    logger.openOutput()

    logger.logPrint("INFO", "Starting MicroSD Card Duplicator [server.py]")

    main(logger)

    logger.logPrint("INFO", "Exiting MicroSD Card Duplicator [server.py]")
    logger.closeMyLog(logger)
