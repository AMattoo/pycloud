# KVM-based Discoverable Cloudlet (KD-Cloudlet)
# Copyright (c) 2015 Carnegie Mellon University.
# All Rights Reserved.
#
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.
#
# Released under a modified BSD license, please see license.txt for full terms.
# DM-0002138
#
# KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
# MiniMongo
# Copyright (c) 2010-2014, Steve Lacy
# All rights reserved. Released under BSD license.
# https://github.com/MiniMongo/minimongo/blob/master/LICENSE
#
# Bootstrap
# Copyright (c) 2011-2015 Twitter, Inc.
# Released under the MIT License
# https://github.com/twbs/bootstrap/blob/master/LICENSE
#
# jQuery JavaScript Library v1.11.0
# http://jquery.com/
# Includes Sizzle.js
# http://sizzlejs.com/
# Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
# Released under the MIT license
# http://jquery.org/license

# Python wrappers for Stanford IBE library

import subprocess

IBE_GEN_EXECUTABLE = "/usr/local/bin/gen"
IBE_CRYPT_EXECUTABLE = "/usr/local/bin/ibe"
IBE_FILES_FOLDER = "/usr/local/etc/ibe"

##############################################################################################################
# Replaces a given string with a new one in the given file.
##############################################################################################################
def replace_in_file(original_text, new_text, filename, folder):
    reg_exp = "s/ " + original_text + ";/ " + new_text + ";/g"
    command = ['/bin/sed', '-i', reg_exp, filename]
    subprocess.Popen(command, cwd=folder)

class LibIBE(object):
    ##############################################################################################################
    # Runs ibe gen command to create master private key and parameters.
    ##############################################################################################################
    def gen(self, private_key_filename, public_key_filename):
        # Set the private key filepath.
        replace_in_file('share', private_key_filename, 'gen.cnf', IBE_FILES_FOLDER)

        # Sets the IBE params file name in the IBE generation config file. This is where the IBE params will be stored.
        replace_in_file('params.txt', public_key_filename, 'gen.cnf', IBE_FILES_FOLDER)

        # Sets the IBE params file in the IBE execution config file. This is so that encryption can find the params.
        replace_in_file('params.txt', public_key_filename, 'ibe.cnf', IBE_FILES_FOLDER)

        # Actually generate the params and master private key.
        subprocess.Popen(IBE_GEN_EXECUTABLE, cwd=IBE_FILES_FOLDER)

    ##############################################################################################################
    # Creates a private key from the given id and master private key ("share"), using the stored IBE params.
    ##############################################################################################################
    def extract(self, id, share):
        privkey = subprocess.check_output([IBE_CRYPT_EXECUTABLE, "extract", id, share], cwd=IBE_FILES_FOLDER)
        return privkey

    ##############################################################################################################
    # Creates a "certificate" hash from the given id and master private key ("share"), using the stored IBE params.
    ##############################################################################################################
    def certify(self, id, share):
        cert = subprocess.check_output([IBE_CRYPT_EXECUTABLE, "certify", id, share], cwd=IBE_FILES_FOLDER)
        return cert
