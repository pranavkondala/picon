#http://stackoverflow.com/questions/21050671/how-to-check-if-device-is-connected-pyserial


import requests,sys,os
import netifaces
import pprint
import ipaddress
import socket
import json
#import serial
import glob
import pyroute2

def getPorts():
  # scan for available ports. return a list of port names with /dev/ stripped off
  ports = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
  ports = [ port.replace('/dev/','') for port in ports ]
  return ports
 
def getInterfaces():
  addrs = {}
  for iface in netifaces.interfaces():
    addrs[iface] = {}
    afs = netifaces.ifaddresses(iface)
    for af in afs:
      if af == netifaces.AF_LINK:
        continue
      for addr in afs[af]:
        # create ipaddress object out of the address
        # however, link-locals have an interface from netifaces
        # and ipaddress does not understand that, so we only take the address
        address = ipaddress.ip_address(addr['addr'].split('%')[0])

	# ipaddress greatly simplifies implementing this logic
        if address.is_loopback or address.is_link_local:
          continue
        addrs[iface].append(str(address))
  return addrs

def getHostname():
  return socket.gethostname()
  
def getSerial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
 
  return cpuserial

def main():

  # buffer to assemble the POST body
  body = {}
  body['hostname'] = getHostname()  
  body['sn'] = getSerial()
  body['interfaces'] = getInterfaces()
  body['ports'] = getPorts()
  headers = {'content-type': 'application/json'}
  jsonbody = json.dumps(body)
  requests.post('http://199.187.221.170:5000/api/register', data = jsonbody, headers = headers)
if __name__ == "__main__":
  main()
