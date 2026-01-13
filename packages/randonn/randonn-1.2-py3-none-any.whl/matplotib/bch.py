# bch.py

def bch_help():
    print(
        '''
    Welcome to the Blockchain Practicals CLI! ⛓️

    This tool allows you to print the code for various blockchain practicals.
    Run any command from your terminal or call its function in Python.

    =========================
    == General Commands    ==
    =========================
    
    Command: bch-help
    Function: bch_help()
    Description: Shows this help message.

    Command: bch-index
    Function: bch_index()
    Description: Displays the full list of blockchain practicals.

    =========================
    == Practical Commands  ==
    =========================

    --- Practical 1: Blockchain Fundamentals ---
    bch-prac-1a      (bch_prac_1a)
    bch-prac-1b      (bch_prac_1b)
    bch-prac-1c      (bch_prac_1c)
        '''
    )

def bch_index():
    print(
        '''
Blockchain Practicals:

1.  Blockchain Fundamentals
    A. .Develop a secure messaging application where users can exchange messages securely using RSA encryption.
        Implement a mechanism for generating RSA key pairs and encrypting/decrypting messages.
    B. Create a Python class named Transaction with attributes for sender, receiver, and amount. 
        Implement a method within the class to transfer money from the sender's account to the receiver's account.
    C. Allow users to create multiple transactions and display them in an organized format.
        '''
    )

def bch_prac_1a():
    print(
        '''
# Client Identity and RSA Encryption

# Part 1: Client Identity Generation
import binascii  
from Crypto import Random  
from Crypto.PublicKey import RSA  
from Crypto.Signature import PKCS1_v1_5  
from Crypto.Hash import SHA  

class Client: 
    def __init__(self):   
        random = Random.new().read 
        self._private_key = RSA.generate(1024, random) 
        self._public_key = self._private_key.publickey() 
        self._signer = PKCS1_v1_5.new(self._private_key)  

    @property 
    def identity(self): 
        return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')  

Demo = Client() 
print(Demo.identity)

# Part 2: RSA Encryption/Decryption
import rsa

publickey, privatekey = rsa.newkeys(512)
message = "Hello World"

encMsg = rsa.encrypt(message.encode(), publickey)
print("Original Message:", message)
print("Encrypted Message:", encMsg)

decMsg = rsa.decrypt(encMsg, privatekey).decode()
print("Decrypted Message:", decMsg)
        '''
    )

def bch_prac_1b():
    print(
        '''
# Transaction Creation and Digital Signatures

import binascii
import datetime
import collections
import Crypto
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

class Client:
    def __init__(self):
        random = Crypto.Random.new().read
        self._private_key = RSA.generate(1024, random)
        self._public_key = self._private_key.publickey()
        self._signer = PKCS1_v1_5.new(self._private_key)

    @property
    def identity(self):
        return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')

class Transaction:
    def __init__ (self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = datetime.datetime.now()

    def to_dict(self):
        if self.sender == "Genesis":
            identity = "Genesis"
        else:
            identity = self.sender.identity

        return collections.OrderedDict({
            'sender': identity,
            'recipient': self.receiver,
            'value': self.amount,
            'time': self.time })

    def sign_transaction(self):
        private_key = self.sender._private_key
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')

def display_transaction(transaction):
    dict = transaction.to_dict()
    print("Sender: " + dict['sender'])
    print("--------------------------")
    print("Receiver: " + dict['recipient'])
    print("--------------------------")
    print("Amount: " + str(dict['value']))
    print("--------------------------")
    print("Time: " + str(dict['time']))
    print("--------------------------")

Bhavesh = Client()
Prabal = Client()
t= Transaction(Prabal, Bhavesh.identity, 2.0)
signature = t.sign_transaction()
print (signature)

print("")
display_transaction(t)
        '''
    )

def bch_prac_1c():
    print(
        '''
# Block Creation and Transaction Management

import binascii
import datetime
import collections
import Crypto
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

class Client:
    def __init__(self):
        random = Crypto.Random.new().read
        self._private_key = RSA.generate(1024, random)
        self._public_key = self._private_key.publickey()
        self._signer = PKCS1_v1_5.new(self._private_key)

    @property
    def identity(self):
        return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')  

class Transaction:
    def __init__ (self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = datetime.datetime.now()

    def to_dict(self):
        if self.sender == "Genesis":
            identity = "Genesis"
        else:
            identity = self.sender.identity

        return collections.OrderedDict({
            'sender': identity,
            'recipient': self.receiver,
            'value': self.amount,
            'time': self.time })

    def sign_transaction(self):
        private_key = self.sender._private_key
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')

class Block:
    def __init__(self):
        self.verified_transactions = []
        self.previous_block_hash = ""
        self.Nonce = ""
    last_block_hash = ""

def display_transaction(transaction):
    dict = transaction.to_dict()
    print("Sender: " + dict['sender'])
    print("--------------------------")
    print("Receiver: " + dict['recipient'])
    print("--------------------------")
    print("Amount: " + str(dict['value']))
    print("--------------------------")
    print("Time: " + str(dict['time']))
    print("--------------------------")

transactions = []

Avanti = Client()
Tanvii = Client()
Keerr = Client()
Nishta = Client()

t1= Transaction(Avanti, Tanvii.identity, 2.0)
t1.sign_transaction()
transactions.append(t1)

t2= Transaction(Tanvii, Nishta.identity, 1.0)
t2.sign_transaction()
transactions.append(t2)

t3= Transaction(Keerr, Tanvii.identity, 2.0)
t3.sign_transaction()
transactions.append(t3)

t4= Transaction(Tanvii, Avanti.identity, 1.0)
t4.sign_transaction()
transactions.append(t4)

t5= Transaction(Nishta, Tanvii.identity, 2.0)
t5.sign_transaction()
transactions.append(t5)

for trans in transactions:
    display_transaction(trans)
    print("#################################")
        '''
    )