from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException

import re
import getpass

#Cisco 2811, Cisco 2901, Cisco 2911, Cisco 3725, Cisco 3745, Cisco 3825, Cisco 3925, Cisco ISR4221 and ISR4451, Cisco 4300, Cisco 3850, Cisco 9k's

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
    'device_type':'cisco_ios',
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
    sh_ver_output = net_connect.send_command('show version')

    #finding hostname in output using regular expressions
    regex_hostname = re.compile(r'(\S+)\suptime')
    hostname = regex_hostname.findall(sh_ver_output)

    #finding uptime in output using regular expressions
    regex_uptime = re.compile(r'\S+\suptime\sis\s(.+)')
    uptime = regex_uptime.findall(sh_ver_output)
    uptime = str(uptime).replace(',' ,'').replace("'" ,"")
    uptime = str(uptime)[1:-1]


    #finding version in output using regular expressions
    regex_version = re.compile(r'Cisco\sIOS\sSoftware.+Version\s([^,]+)')
    version = regex_version.findall(sh_ver_output)

    #finding serial in output using regular expressions
    regex_serial = re.compile(r'Processor\sboard\sID\s(\S+)')
    serial = regex_serial.findall(sh_ver_output)


    #finding model in output using regular expressions
    regex_model = re.compile(r'[Cc]isco\s(\S+).*memory.')
    model = regex_model.findall(sh_ver_output)




    #append results to table [hostname,uptime,version,serial,ios,model]
    devices.append([ip, hostname[0],uptime,version[0], serial[0],model[0]])



#print all results (for all routers) on screen
for i in devices:
    i = ", ".join(i)
    f = open("IOS.csv", "a")
    f.write(i)
    f.write("\n")
    f.close()

