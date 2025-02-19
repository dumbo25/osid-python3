#!/bin/bash
# generic sript to install application where source is stored on github
#
# run using
#    sudo bash [bash_options] install.sh [install_options]

############################# <- 80 Characters -> ##############################
#
# This style of commenting is called a garden bed and it is frowned upon by
# those who know better. But, I like it. I use a garden bed at the top to track
# my to do list as I work on the code, and then mark the completed To Dos.
#
# Within the code, To Dos include a comment with ???, which makes it easy to
# find
#
# Once the To Do list is more-or-less complete, I move the completed items into
# comments, docstrings or help within the code. Next, I remove the completed
# items.
#
# To Do List:
#   a) add uninstall option
#   b) add a2enmod wsgi
#   c) add missing steps to gitClone; perform checks and edits as appropriate
#        Initialize git
#        $ git init
#        Configure git
#        $ git config --global dumbo25.osid-python3 dumbo25
#        $ git config --global dumbo25.email "your-email@gmail.com"
#        $ git config --global core.editor nano
#   d) add django installation instructions, perhaps as a true/false flag and function
#
#   y) add install.sh and install.cfg to github duplicator
#   z) add install.sh and install.cfg to github template
#
# Do later or not at all:
#   - Add option to use different .cfg file
#   - Add option to change username from pi
#   - Add option to change the home directory from /home/pi to something else
#     I rarely do either of the above. So, I am not sure it is worth the effort
#   - I should use lower case for variables and upper case for constants but
#     I run into issues on collisions between lowercase keywords and variables
#   - Add option to suppress output. This is more complex then it should be.
#     exec or redirecting output doesn't work for same for all commands. Some
#     commands like apt have to be suppressed with options like -qq. a suppress
#     option just isn't worth the effort
#   - Add option to change home directory. The home directory should be defined
#     by the username. So, I won't add this as an option.
#   - Add writing to syslog using a logging utility. If this script were running
#     as a cron or in some non-interactive way, then that would make sense. For
#     this script, I do not envision a time when this would not be used in an
#     interactive mode. So, no need to add logging.
#   - Do not make a tmp or install directory and then move files from there. It
#     is easier to just get the files into the correct directory
#   - add list of user defined commands to run at end of the script, but before
#     install. I thought this would be a good add for anything I missed. However,
#     an overarching goal is this script can be run multiple times, each time
#     putting the RPi into a known state. Adding user defined command would be
#     too difficult to backout, unless both an install and a backout command
#     are provided. It might be easier to just do this as needed
#
# Completed:
#   - run script through https://www.shellcheck.net/, which is a lint usitlty for
#     bash shell scripts. Found and fixed all issues as of 09OCT2021.
#
# Naming conventions
#   - lowercase or camelCase for local variable and function names
#   - first uppercase or CamelCase for global variables
#   - all uppercase for ENV variables
#
############################# <- 80 Characters -> ##############################


################################## Functions ###################################
function echoStartingScript {
	if [ "$StartMessageCount" -eq 0 ]
	then
        	echo -e "\n${Bold}Starting Installation Script${Normal}"
                echo "  ${Bold}installing $Name${Normal}"
	        StartMessageCount=1
	fi
}

function echoExitingScript {
        echo -e "\n${Bold}Exiting Installation Script${Normal}"
	# avoid testing if $1 is passed in by using default expansion
	reboot=${1-default}

	if [ "$reboot" = "reboot" ]
	then
            	echo -e "\n${Bold}Rebooting Raspberry Pi in 10s (<CTRL>-C to stop)${Normal}"
                sleep 10s
                sudo reboot
	fi

	exit
}


function help {
	echo "$Help"
}


function makePath {
        if [ ! -d "$1" ]
        then
		if [ "$1" != "" ]
		then
	                echo "    ${Bold}making path: $1${Normal}"
			# -p makes all parent directories if necessary
			mkdir -p "$1"
		fi
        fi
}

function installApt {
	# if there packages to install
	if [[ ${DebianPackages[*]} ]]
	then
		echo -e "\n  ${Bold}installing debian packages${Normal}"
		# loop through all the packages
		for p in "${DebianPackages[@]}"
		do
			# if the package is not already installed
		        notInstalled=$(dpkg-query -W --showformat='${Status}\n' "$p" | grep "install ok installed")
		        if [ "" = "$notInstalled" ]
			then
                                echo "    ${Bold}installing package: $p${Normal}"
                                sudo apt install "$p" -y
		        fi
		done
	else
		echo -e "\n   ${Bold}no raspbian packages in cfg file${Normal}"
	fi
}

function installPip3 {
        # if there packages to install
        if [[ ${Pip3Packages[*]} ]]
        then
                echo -e "\n  ${Bold}installing pip3 packages${Normal}"
                # loop through all the packages
                for p in "${Pip3Packages[@]}"
                do
                        # if the package is not already installed
			notInstalled=$(pip3 list | grep "$p")
		        if [ "$notInstalled" = "" ]; then
        		        echo "    ${Bold}installing pip3: $p${Normal}"
				yes | sudo pip3 install "$p"
		        fi
                done
        else
                echo -e "\n  ${Bold}no pip3 packages in cfg file${Normal}"
        fi
}


function reloadServices {
        # if there are services to reload
        if [[ ${ReloadServices[@]} ]]
        then
                echo -e "\n  ${Bold}reloading services${Normal}"
                # loop through all the packages
                for p in "${ReloadServices[@]}"
                do
                        echo "    ${Bold}$p${Normal}"
			sudo systemctl reload "$p"
                done
        else
                echo -e "\n  ${Bold}no services to reload in cfg file${Normal}"
        fi
}


function restartServices {
        # if there are services to reload
        if [[ ${RestartServices[@]} ]]
        then
                echo -e "\n  ${Bold}restarting services${Normal}"
                # loop through all the packages
                for p in "${RestartServices[@]}"
                do
                        echo "    ${Bold}$p${Normal}"
                        sudo systemctl restart "$p"
                done
        else
                echo -e "\n  ${Bold}no services to restart in cfg file${Normal}"
        fi
}


# GitFile is defined in install.cfg
# I treat gits like apts, egt lastest and overwrite current
function gitFiles {
        # if there are files to git
        if [[ ${GitFiles[@]} ]]
        then
                echo -e "\n  ${Bold}gitting files${Normal}"
                # loop through all the files
                for git in "${GitFiles[@]}"
                do
			# get filename
		        # return string after last slash
		        filename=${git##*/}
                        # if file exists, then need to remove it before wget
		        if [ -f "$filename" ]
		        then
		                echo "    ${Bold}removing file: $filename${Normal}"
		                rm "$filename"
		        fi
		        echo "    ${Bold}gitting file: $filename${Normal}"
		        wget "$git"
                done
        fi
}

# git files from github
# the directory is extracted from the repository
function gitClone {
        if [ $GitClone == ""]
        then
                echo -e "\n  ${Bold}no clones to git${Normal}"
        else
                echo -e "\n  ${Bold}gitting clone: $GitClone${Normal}"
                repository=$GitClone
                # remove ".git"
                repository=${repository::-4}
                # return string after last slash
                directory=${repository##*/}
                if [ -d "$directory" ]
                then
                        echo "    ${Bold}removing directory: $directory${Normal}"
                        rm -rf "$directory"
                fi
                echo -e "\n  ${Bold}gitting clone: $GitClone${Normal}"
                git clone "$GitClone"
        fi
}

# Bash doesn't have multidimensional tables. So, this is my hack to pretend it does
# Each enttry is a row in a table and includes: "filename;fromPath;toPath"
# So, this function moves each row using mv fomPath/filename toPath/."
function moveFiles {
        # if there are files to move
        if [[ ${MoveFiles[*]} ]]
        then
                echo -e "\n  ${Bold}moving files${Normal}"
                # loop through all the packages
                for f in "${MoveFiles[@]}"
                do
                        IFS=';' read -ra file <<< "$f"
			# create path where file will be moved
			makePath "${file[2]}"

			# if the file exists in the fromPath
			if [ -f "${file[1]}/${file[0]}" ]
			then
				# move file fromPath to toPath
		                echo "    ${Bold}mv ${file[1]}/${file[0]} ${file[2]}/. ${Normal}"
				sudo mv "${file[1]}/${file[0]}" "${file[2]}/."
			fi
                done
        fi
}

# The script runs as sudo. So, root ends up owning everything creared. This function
# changes ownership to the correct settings based on the config file.
# Each enttry is a row in a table and includes: "path or path/filename;ownership"
function changeOwnership {
        # if there are files to move
        if [[ ${ChangeOwnership[*]} ]]
        then
                echo -e "\n  ${Bold}changing ownership${Normal}"
                # loop through all the entries
                for f in "${ChangeOwnership[@]}"
                do
                        IFS=';' read -ra file <<< "$f"
                        # if the entry is a file
                        if [ -f "${file[0]}" ]
                        then
                                # change ownership just on the file
                                echo "    ${Bold}chown ${file[0]} to ${file[1]} ${Normal}"
                                chown "${file[1]}" "${file[0]}"
			elif [ -d "${file[0]}" ]
			then
                                # change ownership just on the file
                                echo "    ${Bold}chown rexcursively on ${file[0]} to ${file[1]} ${Normal}"
                                chown -R "${file[1]}" "${file[0]}"
			fi
                done
        fi
}

# The script runs as sudo. So, root ends up owning everything creared. This function
# changes permissions to be correct.
# Each enttry is a row in a table and includes: "path/filename;permissions"
function changePermissions {
        # if there are files to move
        if [[ ${ChangePermissions[*]} ]]
        then
                echo -e "\n  ${Bold}changing permissions${Normal}"
                # loop through all the entries
                for f in "${ChangePermissions[@]}"
                do
                        IFS=';' read -ra file <<< "$f"
                        # if the entry is a file
                        if [ -f "${file[0]}" ]
                        then
                                # change ownership just on the file
                                echo "    ${Bold}chmod ${file[0]} to ${file[1]} ${Normal}"
                                chmod "${file[1]}" "${file[0]}"
                        fi
                done
        fi
}


# Remove files and directories that are not needed
function cleanUp {
        # if there are files to move
        if [[ ${CleanUp[*]} ]]
        then
                echo -e "\n  ${Bold}removing files and directories that are not needed${Normal}"
                # loop through all the entries
                for f in "${CleanUp[@]}"
                do
                        IFS=';' read -ra file <<< "$f"
                        # if the entry is a file
                        if [ -f "${file[0]}" ]
                        then
                                # remove file
                                echo "    ${Bold}remove ${file[0]} ${Normal}"
                                rm "${file[0]}"
                        elif [ -d "${file[0]}" ]
                        then
                                #remove directory
                                echo "    ${Bold}remove rexcursively ${file[0]} ${Normal}"
                                rm -R "${file[0]}"
                        fi
                done
        fi
}


############################### Global Variables ###############################
Bold=$(tput bold)
Normal=$(tput sgr0)
StartMessageCount=0

# I try not to cd in the script. If I do, then it might be good to have the base
# directory
# BaseDirectory=$PWD
Clear=true
Update=true
RebootOn=true
USER=pi
HOME=$(bash -c "cd ~$(printf %q $USER) && pwd")

# Import configuration file for this script
# The config file contains all the apps to install, all the modules to pip3,
# all the files to get, the final path for each, and any permissions required.
# It is basically just a collection of global variables telling the script what
# to do.
if [ -f install.cfg ]
then
        . install.cfg
else
        echoStartingScript
        echo -e "\n  ERROR: Installation script requires $BaseDirectory/install.cfg"
        echo -e "\n    Please wget install.cfg from github or create one."
        echoExitingScript
fi


########################### Start of Install Script  ###########################
# Process command line options
# All options must be listed in order following the : between the quotes on the
# following line:
while getopts ":chru" option
do
	case $option in
		c) # disable clear after update and upgrade
                        Clear=false
                        ;;
		h) # display Help
			help
			exit;;
		r) # disable reboot
			RebootOn=false
			;;
                u) # skip update and upgrade steps
                        Update=false
                        ;;
		*) # handle invalid options
		        echoStartingScript
			echo
		        echo "  ${Bold}ERROR: Invalid option${Normal}"
			echo
			echo "  ${Bold}To see valid options, run using:${Normal}"
			echo
			echo "    \$ sudo bash ${0##*/} -h"
			exit;;
	esac
done


# Exit if not running as sudo or root
if [ "$EUID" -ne 0 ]
then
	echoStartingScript
        echo -e "\n  ${Bold}ERROR: Must run as root or sudo${Normal}"
        echo -e "\n  ${Bold}To see valid options, run using:${Normal}"
        echo -e "\n    \$ sudo bash ${0##*/}"
	exit
fi

# pip3_install fails if errexit is enabled, not sure why
# exit on error
# set -o errexit

# exit if variable is used but not set
set -u
# set -o nounset

# update and uphrade packages
if [ "$Update" = true ]
then
        echoStartingScript

        echo "  ${Bold}updating${Normal}"
        sudo apt update -y
        echo -e "\n  ${Bold}upgrading${Normal}"
        sudo apt upgrade -y
        echo -e "\n  ${Bold}removing trash${Normal}"
        sudo apt autoremove -y

	# the above generates a lot of things that may not be relevant to the install of
	# this application. So, clear the screen and then put Starting message here.
	if [ "$Clear" = true ]
	then
		clear
		StartMessageCount=0
	fi
fi

echoStartingScript

# install required packages, which are defined in DebainPackages list in install.cfg
installApt

# install required python packages, which are defined in PipPackages list in install.cfg
installPip3

# get the all the files from github and create a directory
gitClone

# must check and rm file if it exists before getting a new version
gitFiles

# move files from downloaded path to final path and set permisssions
moveFiles

# change ownership
changeOwnership

# change permissions
changePermissions

# remove files and directories that are not needed
cleanUp

# reload and restart services
reloadServices

restartServices

# print exit message
echo -e "$ExitMessage"

if $RebootOn
then
	if $Reboot
	then
		echoExitingScript reboot
		echo -e "\n${Bold}Rebooting Raspberry Pi in 10s (<CTRL>-C to stop)${Normal}"
		sleep 10s
		sudo reboot
	fi
fi

echoExitingScript
exit
