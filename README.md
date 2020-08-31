# ipwatcher

Ipwatcher is a Python tool useful to check your public IP. When you need to go through a proxy or a VPN if your connection to it goes down, the script will turn off your network manager.
Ipwatcher can also check if your public IP is a TOR node. It can also change your TOR IP using torghost. If your connection is not going through a TOR node, the script will turn off your network manager.

## Setup

sudo apt install torghost

pip3 install requests colored multiprocessing

git clone https://github.com/9426/ipwatcher.git

## Usage

sudo python3 ipwatcher.py

## Contributing

Pull requests are welcome. Feel free to open an issue if you want to add other features.
