from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException

import re
import getpass

#get details from wlc's

#list where informations will be stored
devices = []

#Cred input
user = input("Username: ")
password = getpass.getpass()

#clearing the old data from the CSV file and writing the headers
f = open("IOS.csv", "w+")
f.write("IP Address, Hostname, Uptime, Current_Version, Serial_Number, Device_Model")
f.write("\n")
f.close()

#clearing the old data from the CSV file and writing the headers
f = open("login_issues.csv", "w+")
f.write("IP Address, Status")
f.write("\n")
f.close()

#device.txt file is to be placed in the same folder where script is beeing executed
with open('device.txt') as g:
    ip_list = g.read().splitlines()
#loop all ip addresses in ip_list
for ip in ip_list:
    cisco = {
    'device_type':'cisco_wlc_ssh',
    'ip':ip,
    'username': user,     #ssh username
    'password': password,  #ssh password
    }

    #handling exceptions errors

    try:
        net_connect = ConnectHandler(**cisco)
    except NetMikoTimeoutException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "Device Unreachable/SSH not enabled")
        f.write("\n")
        f.close()
        continue
    except AuthenticationException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "Authentication Failure")
        f.write("\n")
        f.close()
        continue
    except SSHException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "SSH not enabled")
        f.write("\n")
        f.close()
        continue


    # execute show version on router and save output to output object
    sh_run_output = net_connect.send_command('show running-config')
    #finding hostname in output using regular expressions
    regex_hostname = re.compile(r'System Name\.*\s(\S+)')
    hostname = regex_hostname.findall(sh_run_output)
    #finding uptime in output using regular expressions
    regex_uptime = re.compile(r'System Up Time\.*\s(.+)')
    uptime = regex_uptime.findall(sh_run_output)
    uptime = str(uptime).replace(',' ,'').replace("'" ,"")
    uptime = str(uptime)[1:-1]


    #finding version in output using regular expressions
    regex_version = re.compile(r'Product Version\.*\s(.+)')
    version = regex_version.findall(sh_run_output)

    #finding serial in output using regular expressions
    regex_serial = re.compile(r'PID:.*VID:.*SN:\s(\S+)')
    serial = regex_serial.findall(sh_run_output)


    #finding model in output using regular expressions
    regex_model = re.compile(r'PID:\s(\S+),\s+VID:.*SN:.*')
    model = regex_model.findall(sh_run_output)



    #append results to table [hostname,uptime,version,serial,model]
    devices.append([ip, hostname[0],uptime,version[0], serial[0],model[0]])



#print all results (for all routers) on screen
for i in devices:
    i = ", ".join(i)
    f = open("IOS.csv", "a")
    f.write(i)
    f.write("\n")
    f.close()

