#!/usr/bin/env python3
# coding: utf-8
# Version 0.1

import os
import time
import requests
from colored import fore, back, style
#import threading
from multiprocessing import Process, Lock

def check_connection_VPN(previous_ip, previous_interface):

    current_ip = str.rstrip(os.popen('curl -s ifconfig.io').read())
    current_interface = os.popen('ip tuntap show | tail -n 1 | cut -c1-4').read()
    if current_ip != previous_ip and current_interface != previous_interface:
        os.popen('sudo service network-manager stop')
        banner('ip_changed',current_ip, current_interface)
        raise SystemExit
    time.sleep(5)

def check_tor_connection(current_ip):

    r=requests.get(url='https://check.torproject.org/?lang=en')
    r2=requests.get(url='https://www.dan.me.uk/tornodes')
    if 'Sorry. You are not using Tor.' in r.text or 'Forbidden' not in r2.text:
        os.popen('sudo service network-manager stop')
        banner('ip_changed',current_ip)
        raise SystemExit

def tor_ip_changed(current_ip, previous_ip):

    if current_ip != previous_ip and current_ip != '':
        banner('tor_changed', current_ip)
    time.sleep(2)

def change_tor_ip():

    os.popen('sudo torghost -r >/dev/null')

def banner(type, ip=None, interface=None):


    if type == 'tor' or type == 'tor_changing':
        os.system('clear')
        print ("Your " + style.BOLD + "current IP " + style.RESET + "is : " + fore.LIGHT_GREEN + style.BOLD + ip + style.RESET)
        print("If your IP is not a TOR exit node, you will be noticed and the script will turn off your network manager")
        print(fore.LIGHT_GREEN + style.BOLD + "Running..." + style.RESET)

    if type == 'not_tor':
        #os.system('clear')
        print("!!The script will use your last VPN interface")
        print(fore.LIGHT_GREEN + style.BOLD + "Checking VPN network interface and IP..." + style.RESET)
        print ("Your " + style.BOLD + "current IP " + style.RESET + "is : " + fore.LIGHT_GREEN + style.BOLD + ip + style.RESET)
        print ("Your " + style.BOLD + "VPN network interface " + style.RESET + "is : " + fore.LIGHT_GREEN + style.BOLD + str(interface) + style.RESET)
        print("If your IP changes, you will be noticed and the script will turn off your network manager")
        print(fore.LIGHT_GREEN + style.BOLD + "Running..." + style.RESET)

    if type == 'ip_changed':
        t = time.localtime()
        print(fore.RED + style.BOLD + "Your IP just changed at " + style.BOLD + str(time.strftime("%H:%M:%S", t)) + " to " + style.RESET + fore.LIGHT_GREEN + ip + style.RESET)
        print("Turning off network interface ...")
        print(fore.RED + style.BOLD + "Network interface DOWN" + style.RESET)
        print('To restart your network-manager type: ' + fore.BLUE + 'sudo service network-manager start' )

    if type == 'tor_changed':
        print(fore.LIGHT_GREEN + style.BOLD + "TOR IP changing..." + style.RESET)
        print("Your " + style.BOLD + "new TOR IP " + style.RESET + "is : " + fore.LIGHT_GREEN + style.BOLD + ip + style.RESET)
        print(fore.LIGHT_GREEN + style.BOLD + "Running..." + style.RESET)


def check_ip_type():

    print("Are you using TOR? [yY/nN]")
    option = str(input())
    if option == 'y' or option == 'Y':
        r=requests.get(url='https://check.torproject.org/?lang=en')
        r2=requests.get(url='https://www.dan.me.uk/tornodes')
        if 'Sorry. You are not using Tor.' in r.text and 'Forbidden' not in r2.text:
            print(fore.RED + style.BOLD + "You should first connect to a TOR node before running this script" + style.RESET)
            print ("Bye")
            raise SystemExit
        else:

            print("Would you like to change your TOR IP every ~7 seconds? [yY/nN]")
            print(fore.RED + style.BOLD + "You will need to install and use torghost first" + style.RESET)
            print(fore.RED + style.BOLD + "https://github.com/SusmithKrishnan/torghost.git" + style.RESET)
            option = str(input())
            if option == 'y' or option == 'Y':
                return 'tor_changing'
            if option == 'n' or option == 'N':
                return 'tor'
            else:
                print('Wrong input')

    if option == 'n' or option == 'N':
        return 'not_tor'
    else:
        print('Wrong input')

def options(current_ip):

    os.system('clear')
    print ("Your current IP is : " + fore.LIGHT_GREEN + style.BOLD + current_ip + style.RESET)
    print ("What do you want to do?")
    print ("   1) Check my current IP while working")
    print ("   2) Exit")
    option = input()
    if option == '1':
        return check_ip_type()
    if option == '2':
        raise SystemExit
    else:
        print('Wrong input')

def main():

    global ip_type
    t = 0
    current_ip = str.rstrip(os.popen('curl -s ifconfig.io').read())
    current_interface = os.popen('ip tuntap show | tail -n 1 | cut -c1-4').read()

    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
        raise SystemExit

    ip_type = options(current_ip)
    banner(ip_type, current_ip, current_interface)
    while True:
        try:
            if ip_type == 'tor_changing':

                t1 = Process(check_tor_connection(current_ip))
                t1.start()
                previous_ip = current_ip
                current_ip = str.rstrip(os.popen('curl -s ifconfig.io').read())
                tor_ip_changed(current_ip, previous_ip)
                t2 = Process(target=change_tor_ip())
                t = t+1
                if t ==3:
                    t2.start()
                    #t2_pid = t2.pid
                    t2.join()
                    t2.terminate()
                    t = 0

            if ip_type == 'tor':
                check_tor_connection(current_ip)
                previous_ip = current_ip
                current_ip = str.rstrip(os.popen('curl -s ifconfig.io').read())
                tor_ip_changed(current_ip, previous_ip)

            else:
                check_connection_VPN(current_ip, current_interface)

        except requests.exceptions.ConnectTimeout:
            t = time.localtime()
            print(fore.RED + style.BOLD + "Got a timeout from the TOR IP check at " + style.BOLD + str(time.strftime("%H:%M:%S", t)) + style.RESET)
            print("Turning off network interface ...")
            os.popen('sudo service network-manager stop')
            print(fore.RED + style.BOLD + "Network interface DOWN" + style.RESET)
            print('To restart your network-manager type: ' + fore.BLUE + 'sudo service network-manager start' )
            raise SystemExit

        except requests.exceptions.RequestException:
            t = time.localtime()
            print(fore.RED + style.BOLD + "Unable to verify your TOR IP at " + style.BOLD + str(time.strftime("%H:%M:%S", t)) + style.RESET)
            print("Turning off network interface ...")
            os.popen('sudo service network-manager stop')
            print(fore.RED + style.BOLD + "Network interface DOWN" + style.RESET)
            print('To restart your network-manager type: ' + fore.BLUE + 'sudo service network-manager start' )
            raise SystemExit


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        if ip_type == 'tor_changing':
            os.popen('sudo killall torghost >/dev/null')
        raise SystemExit
