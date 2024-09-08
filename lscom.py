#!/usr/bin/python3

import serial.tools.list_ports
from sys import argv,exit



def printpair(name,val):
  if val==None: return
  if val=='': return
  if name!='': name+=':'
  print(f'{name:>16} {val}')


def getfuseropened(dev):
   if noexec: return ''
   import subprocess
   arg=['fuser','-v',dev]
   try:
     printtrace('exec:',arg)
     proc = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
     proc.wait()
     opid = proc.stdout.read()
     o = proc.stderr.read()
     if o==b'': return ''
     o=o.decode('utf-8')
     while '  ' in o: o=o.replace('  ',' ')
     aa=o.split('\n')
     if len(aa)<2: return ''
     a=aa[1].split(' ')
     if len(a)<4: return str(a)
     opid=opid.decode('utf-8').strip()
     cmd=' '.join(a[3:])
     s=f'{cmd}     flags={a[2]} PID={opid} USER={a[1]} PORT={a[0]}'
     return s
   except Exception as e:
     return 'ERR: fuser exec: '+str(e)


def getuptime():
  try:
    with open('/proc/uptime', 'r') as f:
      return float(f.readline().split()[0])
  except: return None

def age2str(n):
  if n<0: ss='-'
  else: ss=''
  if n<0 and n>-30: return '0s' # for boot ages
  n=abs(n)
  d=int(n/3600/24)
  h=int((n%(3600*24))/3600)
  m=int((n%3600)/60)
  s=int(n%60)
  #ss+=str(d)+'d'+str(h)+'h'
  if d>0: ss+=str(d)+'d'
  if d>0 or h>0: ss+=str(h)+'h'
  ss+=str(m)+'m'+str(s)+'s'
  return ss

def printdevage(dev):
#  uptime=getuptime()
#  if uptime==None: return None
  from os import stat
  from time import time
  if dev=='' or dev==None: return
  modtime=stat(dev).st_ctime
  boottime=stat('/dev/mem').st_ctime
  now=time()
  age=now-modtime
  bootage=modtime-boottime
  uptime=now-bootage
  #print('XXX',dev,age2str(age),age2str(now-uptime),age2str(bootage))
  #agestr=age2str(age)+' (boot+'+age2str(modtime-boottime)+')'
  agestr=age2str(age)
  if abs(bootage)<30: agestr+=' (present at startup)'
  printpair('age',agestr)
  #printpair('age',age2str(age))
  #printpair('bootage',age2str(modtime-uptime))


"""
[/sys/devices/virtual/tty/rfcomm0/]
address 00:15:a3:00:35:ec
channel 1
dev     216:0
subsystem:      -> ../../../../class/tty
uevent  MAJOR=216
        MINOR=0
        DEVNAME=rfcomm0

[root@disp:~]# rfcomm
rfcomm0: 00:15:A3:00:CE:21 channel 1 closed
"""

proc_rfcomm=[]
proc_btctl=[]

def printerr(*s):
  if verb: print('ERR:',*s)

def printtrace(*s):
  if trace: print('TRACE:',*s)


# get line containing the string from a list
def getlinestr(arr,s):
   for x in arr:
     if s.upper() in x.upper(): return x
   return None

# excecute "rfcomm" and "bluetootctl devices" 
def readbluetoothdetails():
   global proc_rfcomm,proc_btctl
   if noexec: return
   if len(proc_rfcomm)>0 or len(proc_btctl)>0: return
   import subprocess
   try:
     arg=['rfcomm']
     printtrace('exec:',arg)
     proc = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
     proc.wait()
     o = proc.stdout.read().decode('utf-8')
     oerr = proc.stderr.read()
     #print('err:',oerr)
     proc_rfcomm=o.split('\n')
   except Exception as e:
     proc_rfcomm=['']
     printerr('rfcomm exec:',e)
   try:
     arg=['bluetoothctl','devices']
     printtrace('exec:',arg)
     proc = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
     proc.wait()
     o = proc.stdout.read().decode('utf-8')
     oerr = proc.stderr.read()
     #print('err:',oerr)
     proc_btctl=o.split('\n')
   except Exception as e:
     proc_btctl=['']
     printerr('bluetoothctl exec:',e)


# get rfcomm port data from /sys
def getrfcommdetails(dev):
   a={}
   a['']='BLUETOOTH'
   try:
     path='/sys/devices/virtual/tty/'+dev+'/address'
     printtrace('reading property from',path)
     with open(path,'r') as f: a['BT_address']=f.readline().strip()
   except Exception as e: printerr('/sys/.../address access:',e)
   try:
     path='/sys/devices/virtual/tty/'+dev+'/channel'
     printtrace('reading property from',path)
     with open(path,'r') as f: a['BT_channel']=f.readline().strip()
   except Exception as e: printerr('/sys/.../channel access:',e)
   return a



# print data about the port
def printport(p,links={},bylines=False,all=False,showopen=False):
  #print(dir(p))
  if bylines:
#    prod=p.get('product','')
    if p.get('name','')[:6]=='rfcomm':
      try: a=getrfcommdetails(p.name);prod=a['BT_address']
      except Exception as e: printerr('rfcomm call:',e)
    print(f'{p.get("device")}|{p.get("name")}|{p.get("subsystem")}|{p.get("hwid")}|{p.get("product","")}')

  else:
    lval=links.values()
    linked=[]
    for x in links:
      if links[x]==p.get("device"): linked.append(x)
    #print(p.device,linked)
    if (not all) and (p.get("device") in links): return # skip links

    print(p.get("device"))
    for x in linked: print('=',x)

    if showopen: printpair('OPENED BY',getfuseropened(p.get('device')))

    v=p
    items=['device','name','subsystem','interface','*age','description','product','manufacturer','serial_number','vid','pid','location','hwid','device_path']
    for x in v:
      if x not in items: items.append(x)

    if not all:
      if v.get('interface')==v.get('product'): items.remove('interface')
      if v.get('description')==v.get('name'): items.remove('description')
      if v.get('interface')!=None and v.get('product')!=None and v.get('description')==v.get('interface')+' - '+v.get('product'): items.remove('description')
      items.remove('device')
    else:
      items=sorted(items)

    # print individual items in the list
    for x in items:
      if x=='*age': # show how old the file item is
        try: printdevage(v.get('device'));continue
        except: continue
      if x not in v: continue # windows miss sybsystem, device_path
      if v[x]==None: continue
      if v[x]=='n/a': continue
      if x=='vid': continue
      if x=='pid': printpair('VID:PID',f'{p.get("vid"):04x}:{p.get("pid"):04x}');continue
      printpair(x,v[x])

    if v['name'][:6]=='rfcomm':
      a=getrfcommdetails(v['name'])
      for x in a: printpair(x,a[x])
      readbluetoothdetails()
      printpair('rfcomm',getlinestr(proc_rfcomm,v['name']+':'))
      if 'BT_address' in a: printpair('bluetoothctl',getlinestr(proc_btctl,a['BT_address']))
    print()



# read symlinks from list of directories
def getdirlinks(paths=['/dev','/dev/serial/by-path','/dev/serial/by-id']):
  import os
  a={}
  for path in paths:
    try:
      printtrace('reading symlinks from',path)
      for name in os.listdir(path):
        if name not in (os.curdir, os.pardir):
          full = os.path.join(path, name)
          if os.path.islink(full):
            a[full]=os.path.realpath(full)
    except FileNotFoundError: pass
  #print('FS links:',a)
  return a


# get links from array of ports
def getlinks(portarr):
#  try:
  links=getdirlinks()
#  except Exception as e:
#    printerr('warn: getdirlinks() failed:',e)
#    links={} # SILENT FAIL ERROR
  for pdev in portarr:
    p=portarr[pdev]
    if 'LINK=' not in p.get('hwid'): continue
    a=p.get('hwid','').split(' ')
    if a[0][:5]=='LINK=': links[p.get('device')]=a[0][5:]

  return links


# list all serial ports by alternative approach
def alt_serial_ports():
    # from https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
    import sys
    from glob import glob
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    skipports=['/dev/ttyprintk']

    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        if port in skipports: continue
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result




# obtain list of ports, read symlinks, print them all
def printports(bylines=False,all=False,showopen=False,altscan=True):
  printtrace('getting port list from serial.tools.list_ports.comports()')
  ports={}
  for x in list(serial.tools.list_ports.comports()):
    ports[x.device]=vars(x)

  #ports['/dev/ttyAMA0']={'device': '/dev/ttyAMA0', 'name': 'ttyAMA0', 'description': 'ttyAMA0', 'hwid': '107d001000.serial', 'vid': None, 'pid': None, 'serial_number': None, 'location': None, 'manufacturer': None, 'product': None, 'interface': None, 'usb_device_path': None, 'device_path': '/sys/devices/platform/soc/107d001000.serial', 'subsystem': 'amba', 'usb_interface_path': None}
  if altscan:
    try: altports=alt_serial_ports()
    except: altports=[];print('alt port scan failed')
    for x in altports:
      if x in ports: continue
      ports[x]={'device':x,'name':x.split('/')[-1],'description':'from alt scan','hwid':'altscan:'+x}

  links=getlinks(ports)
  for p in sorted(ports): printport(ports[p],links=links,bylines=bylines,all=all,showopen=showopen)
  #getrfcomm()


def printaltports():
  for x in sorted(alt_serial_ports()):
    print(x)



def help():
  print("""List serial ports available on the machine.
Usage: """+argv[0]+""" [-l] [-h]
Where:
  -l       list format, one port per line
  -L       list by alternative scan
  -N       skip alternative scan
  -a       show all port properties, alphabetically, no filtering
  -o       show process that has the port opened (call fuser -v)
  -noexec  do not execute any commands as helpers (rfcomm, bluetoothctl)
  -d       debug, trace the operations performed
  -h       help
""")
  exit(0)


bylines=False
all=False
showopen=False
noexec=False
verb=True
trace=False
altscan=True
if len(argv)>1:
  if argv[1] in ['help','-h','--help']: help()
  if '-l' in argv: bylines=True
  if '-L' in argv: printaltports();exit(0)
  if '-N' in argv: altscan=False
  if '-a' in argv: all=True
  if '-o' in argv: showopen=True
  if '-d' in argv: trace=True
  if '-noexec' in argv: noexec=True

printports(bylines=bylines,all=all,showopen=showopen,altscan=altscan)


