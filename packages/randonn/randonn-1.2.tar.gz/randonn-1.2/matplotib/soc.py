# SOC

def soc_help():
    print(
        '''
    Welcome to the SOC Practicals CLI! 🔒

    This tool allows you to print the commands for various SOC practicals.
    Run any command from your terminal or call its function in Python.

    =========================
    == General Commands    ==
    =========================
    
    Command: soc-help
    Function: soc_help()
    Description: Shows this help message.

    Command: soc-index
    Function: soc_index()
    Description: Displays the full list of SOC practicals.

    =========================
    == Practical Commands  ==
    =========================

    --- Practical 1: Encryption & Decryption ---
    soc-prac-1a      (soc_prac_1a)
    soc-prac-1b      (soc_prac_1b)
    soc-prac-1c      (soc_prac_1c)

    --- Practical 2: Network Analysis ---
    soc-prac-2a      (soc_prac_2a)

    --- Practical 3: PCAP Analysis ---
    soc-prac-3b      (soc_prac_3b)
    soc-prac-3c      (soc_prac_3c)

    --- Practical 4: Traffic Analysis ---
    soc-prac-4a      (soc_prac_4a)
    soc-prac-4b      (soc_prac_4b)

    --- Practical 5: Database Attacks ---
    soc-prac-5a      (soc_prac_5a)

    --- Practical 6: Syslog Server ---
    soc-prac-6a      (soc_prac_6a)

    --- Practical 7: Syslog Configuration ---
    soc-prac-7a      (soc_prac_7a)

    --- Practical 8: Splunk ---
    soc-prac-8a      (soc_prac_8a)

    --- Practical 9: ELK Stack ---
    soc-prac-9a      (soc_prac_9a)

    --- Practical 10: GrayLog ---
    soc-prac-10a     (soc_prac_10a)
        '''
    )

def soc_index():
    print(
        '''
Security Operations Center (SOC) Practicals:

1.  Encryption and Decryption
    A. Encrypting and Decrypting Data Using a Hacker Tool
    B. Encrypting and Decrypting Data Using OpenSSL
    C. Hashing a Text File With OpenSSL and Verifying Hashes

2.  Network Analysis
    A. Examining Telnet and SSH in Wireshark

3.  PCAP Analysis
    B. Extract an Executable from a PCAP
    C. Exploring DNS Traffic

4.  Traffic Analysis
    A. Using Wireshark to Examine HTTP and HTTPS traffic
    B. Exploring Processes, Threads, Handles, and Windows Registry

5.  Database Attacks
    A. Attack on a MySQL Database by using PCAP file

6.  Syslog Server
    A. Create your own syslog Server

7.  Syslog Configuration
    A. Configure your Linux system to send syslog messages to a syslog server

8.  Splunk
    A. Install and run Splunk on Linux

9.  ELK Stack
    A. Install and Configure ELK on Linux

10. GrayLog
    A. Install and Configure GrayLog on Linux
        '''
    )

def soc_prac_1a():
    print(
        '''
# Encrypting and Decrypting Data Using a Hacker Tool

# Step 1: Create a folder named: zip-files and move to that folder
mkdir zip-files
cd zip-files

# Step 2: Create sample files inside this folder and add text
echo "Sample content" > sample1.txt
echo "More content" > sample2.txt

# Step 3: Creating Encrypted Zip Files
zip -e file-1.zip sample*

# Step 4: Cracking Zip Passwords with fcrackzip using Brute Force
man fcrackzip

# Command to crack password:
fcrackzip -vul 1-4 file-1.zip

# Command to unzip:
unzip file-1.zip
        '''
    )

def soc_prac_1b():
    print(
        '''
# Encrypting and Decrypting Data Using OpenSSL

# Step 1: Access the letter_to_grandma.txt file from the lab.support.files folder
cd lab.support.files/
ls
cat letter_to_grandma.txt

# Step 2: Encrypt the file and verify
openssl aes-256-cbc -in letter_to_grandma.txt -out message.enc

ls
cat message.enc

# Alternative command:
openssl aes-256-cbc -a -in letter_to_grandma.txt -out message.enc

# Step 3: Decrypt the file and verify
openssl aes-256-cbc -d -a -in message.enc -out letter.txt
        '''
    )

def soc_prac_1c():
    print(
        '''
# Hashing a Text File With OpenSSL and Verifying Hashes

# Create another file naming as letter_to_grandpa.txt in the lab.support.files folder
# And paste the content from the letter_to_grandma.txt to the letter_to_grandpa.txt

# Command for hashing the content (SHA256):
openssl sha256 letter_to_grandma.txt

# Command for hashing the content (SHA512):
openssl sha512 letter_to_grandma.txt

# Hash the second file to compare:
openssl sha256 letter_to_grandpa.txt
openssl sha512 letter_to_grandpa.txt

# Note: Files with same content will have matching hashes
# Change content of letter_to_grandpa.txt to see different hashes
        '''
    )

def soc_prac_2a():
    print(
        '''
# Examining Telnet and SSH in Wireshark

# Telnet Analysis:
# 1. Double click and open Wireshark from the virtual machine's desktop
# 2. Select the loopback: lo interface → right click → select start capture

# Open the terminal and run:
telnet localhost
# Enter username: analyst and password: cybercops

# In Wireshark:
# - Select any packet → right-click, and choose Follow → TCP Stream
# - The username and password will be displayed in plain text

# SSH Analysis:
# 1. Double click and open Wireshark from the virtual machine's desktop
# 2. Select the loopback: lo interface → right click → select start capture

# Open the terminal and run:
ssh localhost
# Enter password: cybercops when prompted

# In Wireshark:
# - Select any packet → right-click, and choose Follow → TCP Stream
# - The username and password will appear in an encrypted format
        '''
    )

def soc_prac_3b():
    print(
        '''
# Extract an Executable from a PCAP

# Steps:
# 1. Open the pcap file in Wireshark
# 2. Locate the relevant TCP stream transferring the executable, often identified by HTTP GET or FTP data
# 3. Right-click the packet and select "Follow TCP Stream" to view the file transfer content
# 4. In the TCP Stream window, set "Show data as" to "Raw" and click "Save as..." to export the raw data as a file
# 5. Alternatively, go to "File" > "Export Objects" > select the protocol (HTTP/FTP) and save the executable from the displayed list
        '''
    )

def soc_prac_3c():
    print(
        '''
# Exploring DNS Traffic

# In Windows CMD:
# Command for flushing dns
ipconfig /displaydns
ipconfig /flushdns

# Command to flush dns in Linux:
systemctl status systemd-resolved.service
sudo systemctl restart systemd-resolved.service

# Then open Wireshark:
# 1. Identify that 10.0.2.2 is the device IP as it is a private IP address
# 2. Browse 2 sites
# 3. In Wireshark, filter DNS by typing "udp.port==53" or "udp" as UDP port number is 53

# Analyze the following:
# - IP address
# - MAC address
# - Host port No.
# - DNS port No. (53)
# - DNS Flags
# - DNS response and Query
# - CNAME and A records

# Pick the response and queries and analyze the data
        '''
    )

def soc_prac_4a():
    print(
        '''
# Using Wireshark to Examine HTTP and HTTPS traffic

# HTTP Analysis:
# 1. Select the enp0s3 interface -- right click -- select start capture
# 2. Use testing website (Altoro manual login jsp)
# 3. Enter dummy username and password

# Checking HTTP requests:
# - Filter HTTP requests only
# - Check for POST request and click on it
# - In the second window under the HTML form you'll get the username and password in plain text

# HTTPS Analysis:
# - For filtering HTTPS requests: tcp.port == 443
# - Select the Application Data under Transport Layer Security
# - You'll get Encrypted Application Data
        '''
    )

def soc_prac_4b():
    print(
        '''
# Exploring Processes, Threads, Handles, and Windows Registry

# 1. Open SysinternalsSuite which contains various tools
# 2. Open procexp64

# This is similar to task manager where we can see current tasks and also kill them
# Try to ping something in cmd and you can see a process under cmd and then kill itself
# Here we can see the handlers and threads

# Registry Editor:
# 1. Type windows+r and type regedit to open registry editor
# 2. Here the various footprints are stored
# 3. We can see here we accepted EULA (End user license agreement)
# 4. The value 1 means we agreed the license which we accepted when we started the procexp64
# 5. If we change it to 0 then we'll be prompted again for accepting license when we start it
        '''
    )

def soc_prac_5a():
    print(
        '''
# Attack on a MySQL Database by using PCAP file

# Note: This practical involves analyzing PCAP files for MySQL database attacks
# Specific implementation details would depend on the provided PCAP file
        '''
    )

def soc_prac_6a():
    print(
        '''
# Create your own syslog Server

# Step 1: Check whether rsyslog services already running or not
sudo systemctl status rsyslog

# Step 2: Install rsyslog if not installed or running
sudo apt-get update
sudo apt-get install rsyslog

# Step 3: Open rsyslog configuration file
sudo nano /etc/rsyslog.conf

# Step 4: Uncomment the four lines that enable UDP and TCP port binding

# Step 5: Add template right before GLOBAL DIRECTIVES section
# $template remote-incoming-logs,"/var/log/%HOSTNAME%/%PROGRAMNAME%.log"
# *.* ?remote-incoming-logs

# Step 6: Save and restart rsyslog service
sudo systemctl restart rsyslog

# Step 7: Confirm that rsyslog service is listening on configured ports
ss -tunelp | grep 514

# Step 8: Allow rsyslog firewall port rules
sudo ufw allow 514/tcp
sudo ufw allow 514/udp

# Step 9: To verify configuration, run the following command
sudo rsyslogd -N1 -f /etc/rsyslog.conf
        '''
    )

def soc_prac_7a():
    print(
        '''
# Configure your Linux system to send syslog messages to a syslog server

# Step 1: Install and configure rsyslog server first (refer practical no 6)

# Step 2: Install rsyslog
sudo apt-get update
sudo apt-get install rsyslog

# Step 3: Open rsyslog configuration file
sudo nano /etc/rsyslog.conf

# Step 4: Add below lines at the end of the file
# @192.168.137.50:514
# *.* action(
#     type="omfwd"
#     target="192.168.137.50"
#     port="514"
#     protocol="tcp"
#     action.resumeRetryCount="-1"
#     queue.filename="forwarding"
#     queue.maxDiskSpace="1g"
#     queue.saveOnShutdown="on"
#     queue.type="LinkedList"
# )

# Step 6: Save and exit the file

# Step 7: Restart the rsyslog service
sudo systemctl restart rsyslog

# Step 8: Go to your Rsyslog server to verify the logs from your client machine
ls /var/log/

# Step 9: To check logs use the following command
sudo tail -f /var/log/labvm/rsyslogd.log
        '''
    )

def soc_prac_8a():
    print(
        '''
# Install and run Splunk on Linux

# Step 1: Download Splunk Installer
cd /tmp && wget https://download.splunk.com/products/splunk/releases/7.1.1/linux/splunk-7.1.1-8f0ead9ec3db-linux-2.6-amd64.deb

# Step 2: Install Splunk
sudo dpkg -i splunk-7.1.1-8f0ead9ec3db-linux-2.6-amd64.deb

# Step 3: Enable the Splunk to start at boot
# Press enter key till you reach to the end of the agreement
# Accept the license agreement by typing "y"
# Enter the initial admin password
sudo /opt/splunk/bin/splunk enable boot-start
# Password: admin@123

# Step 4: Start the Splunk service
sudo service splunk start

# Step 5: Check splunk service Status
sudo service splunk status

# Step 6: Access Splunk
# Splunk will be started at port 8000
# Access via URL: http://localhost:8000/
# Username: admin
# Password: admin@123
        '''
    )

def soc_prac_9a():
    print(
        '''
# Install and Configure ELK on Linux

# Step 1: Update and install JDK
sudo apt update

# Install Java
sudo apt install default-jre

# Step 2: Check the Java version
java --version

# Part 2: Install and Configure Elasticsearch

# Step 1: Download and install the GPG signing key
curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -

# Step 2: Set up the Elasticsearch repository
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list

# Step 3: Update the repository cache and install Elasticsearch
sudo apt update
sudo apt install elasticsearch

# Step 4: Edit the Elasticsearch configuration file
sudo nano /etc/elasticsearch/elasticsearch.yml
# Uncomment: network.host: localhost
# Uncomment: http.port: 9200

# Step 5: Start the Elasticsearch service
sudo systemctl start elasticsearch
sudo systemctl status elasticsearch

# Step 6: Enable Elasticsearch to start at boot
sudo systemctl enable elasticsearch

# Step 7: Test Elasticsearch service
curl -X GET "localhost:9200"
        '''
    )

def soc_prac_10a():
    print(
        '''
# Install and Configure GrayLog on Linux

# Step 1: Install Java and Elasticsearch (Practical 9)

# Step 2: Edit the Elasticsearch configuration file for Graylog
sudo nano /etc/elasticsearch/elasticsearch.yml

# Step 3: Set the cluster name as graylog and add:
# cluster.name: graylog
# action.auto_create_index: false

# Step 4: Start the Elasticsearch service
sudo systemctl daemon-reload
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch

# Step 5: Check Elasticsearch response
curl -X GET http://localhost:9200

# Step 6-10: Install MongoDB 6.0

# Step 7: Add MongoDB 6.0 GPG key
curl -fsSL https://pgp.mongodb.com/server-6.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor

# Step 8: Add MongoDB 6.0 repo
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Step 9: Update and install MongoDB
sudo apt update
sudo apt install -y mongodb-org

# Step 10: Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
sudo systemctl status mongod

# Step 11-21: Install GrayLog Server

# Step 12: Download and install Graylog repository
wget https://packages.graylog2.org/repo/packages/graylog-4.2-repository_latest.deb
sudo dpkg -i graylog-4.2-repository_latest.deb

# Step 13: Update repository cache
sudo apt update

# Step 14: Install Graylog server
sudo apt install -y graylog-server

# Step 15: Generate secret
sudo apt install pwgen
pwgen -N 1 -s 96

# Step 16: Edit Graylog Configuration File
sudo nano /etc/graylog/server/server.conf

# Step 17: Generate SHA256 hash password for root user
echo -n mypassword | sha256sum

# Step 18: Setup Graylog web interface
sudo nano /etc/graylog/server/server.conf
# Add:
# http_bind_address = 127.0.0.1:9000
# http_external_uri = http://localhost:9000/

# Step 19: Start and enable Graylog service
sudo systemctl daemon-reload
sudo systemctl start graylog-server
sudo systemctl enable graylog-server

# Step 20: Monitor Graylog server startup logs
sudo tail -f /var/log/graylog-server/server.log

# Step 21: Access Graylog
# Open browser and go to: http://localhost:9000
        '''
    )