#!/usr/bin/env python3
# coding: utf-8
# Version 0.1

import os
import time
import requests
from colored import fore, back, style
import threading

def check_connection(ip_type, t2=None):
    global current_ip

    if ip_type == 'tor' or ip_type == 'tor_changing':
        r=requests.get(url='https://check.torproject.org/?lang=en')
        r2=requests.get(url='https://www.dan.me.uk/tornodes')
        if 'Sorry. You are not using Tor.' in r.text or 'Forbidden' not in r2.text:
            os.popen('sudo service network-manager stop')
            previous_ip = str.rstrip(os.popen('curl -s ifconfig.io').read())
            banner('ip_changed',previous_ip)
            t2.join()
            raise SystemExit
        else:
            previous_ip = str.rstrip(os.popen('curl -s ifconfig.io').read())
            if current_ip != previous_ip and previous_ip != '':
                print(fore.LIGHT_GREEN + style.BOLD + "TOR IP changing..." + style.RESET)
                current_ip = previous_ip
                print("Your " + style.BOLD + "new TOR IP " + style.RESET + "is : " + fore.LIGHT_GREEN + style.BOLD + current_ip + style.RESET)
                print(fore.LIGHT_GREEN + style.BOLD + "Running..." + style.RESET)
            time.sleep(2)

    if ip_type == 'not_tor':
        previous_ip = str.rstrip(os.popen('curl -s ifconfig.io').read())
        interface = os.popen('ip tuntap show | cut -c1-4').read()
        if current_ip != previous_ip and interface == '':
            interface = os.popen('ip tuntap show | cut -c1-4').read()
            banner('ip_changed',previous_ip)
            raise SystemExit
        time.sleep(5)

def change_tor_ip():

    os.popen('sudo torghost -r >/dev/null')

def banner(type, ip=None):

    if type == 'tor' or type == 'tor_changing':
        os.system('clear')
        print ("Your " + style.BOLD + "current IP " + style.RESET + "is : " + fore.LIGHT_GREEN + style.BOLD + current_ip + style.RESET)
        print("If your IP is not a TOR exit node, you will be noticed and the script will turn off your network manager")
        print(fore.LIGHT_GREEN + style.BOLD + "Running..." + style.RESET)

    if type == 'not_tor':
        os.system('clear')
        print("The script will use your first VPN interface, it will not work well if you use several VPNs at the same time")
        print(fore.LIGHT_GREEN + style.BOLD + "Checking VPN network interface and IP..." + style.RESET)
        print ("Your " + style.BOLD + "current IP " + style.RESET + "is : " + fore.LIGHT_GREEN + style.BOLD + current_ip + style.RESET)
        print ("Your " + style.BOLD + "VPN network interface " + style.RESET + "is : " + fore.LIGHT_GREEN + style.BOLD + interface + style.RESET)
        print("If your IP changes, you will be noticed and the script will turn off your network manager")
        print(fore.LIGHT_GREEN + style.BOLD + "Running..." + style.RESET)

    if type == 'ip_changed':
        t = time.localtime()
        print(fore.RED + style.BOLD + "Your IP just changed at " + style.BOLD + str(time.strftime("%H:%M:%S", t)) + " to " + style.RESET + fore.LIGHT_GREEN + ip + style.RESET)
        print("Turning off network interface ...")
        print(fore.RED + style.BOLD + "Network interface DOWN" + style.RESET)
        print('To restart your network-manager type: ' + fore.BLUE + 'sudo service network-manager start' )


def ip_type():

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

            print("Would you like to change your TOR IP every 15 seconds? [yY/nN]")
            print(fore.RED + style.BOLD + "You will need to install and use torghost first" + style.RESET)
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

def options():

    os.system('clear')
    print ("Your current IP is : " + fore.LIGHT_GREEN + style.BOLD + current_ip + style.RESET)
    print ("What do you want to do?")
    print ("   1) Check my current IP while working")
    print ("   2) Exit")
    option = input()
    if option == '1':
        return ip_type()
    if option == '2':
        raise SystemExit
    else:
        print('Wrong input')

def main():

    global current_ip
    global ip_type
    t = 0
    current_ip = str.rstrip(os.popen('curl -s ifconfig.io').read())

    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
        raise SystemExit

    ip_type = options()
    banner(ip_type)
    while True:
        try:
            if ip_type == 'tor_changing':

                t2 = threading.Thread(name='daemon1', target=change_tor_ip())
                t1 = threading.Thread(name='daemon2', target=check_connection(ip_type, t2))
                t1.setDaemon(True)
                t2.setDaemon(True)
                t1.start()
                t = t+1
                if t ==3:
                    t2.start()

            else:
                check_connection(ip_type)

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
        print ("\n Bye1")
        raise SystemExit
