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
__author__ = 'Sebastian'

from pycloud.pycloud.mongo import Model, ObjectID

# ###############################################################################################################
# Represents a device authorized into the system.
################################################################################################################
class PairedDevice(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "paired_devices"
        external = ['_id', 'device_id', 'connection_id', 'auth_start', 'auth_duration', 'auth_enabled']
        mapping = {
        }

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self.device_id = None
        self.connection_id = None
        self.auth_start = None
        self.auth_duration = 0
        self.auth_enabled = False
        super(PairedDevice, self).__init__(*args, **kwargs)

    ################################################################################################################
    # Locate a device by its internal DB ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_internal_id(sid=None):
        rid = sid
        if not isinstance(rid, ObjectID):
            # noinspection PyBroadException
            try:
                rid = ObjectID(rid)
            except:
                return None
        return PairedDevice.find_one({'_id': rid})

    ################################################################################################################
    # Locate a device by its pubilc device ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_id(sid=None):
        try:
            device = PairedDevice.find_one({'device_id': sid})
        except:
            return None
        return device

    ################################################################################################################
    # Locate a device by its connection ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_connection_id(id=None):
        try:
            device = PairedDevice.find_one({'connection_id': id})
        except:
            return None
        return device

    ################################################################################################################
    # Cleanly and safely gets a Device and removes it from the database
    ################################################################################################################
    @staticmethod
    def find_and_remove(sid):
        # Find the right device and remove it. find_and_modify will only return the document with matching id
        return PairedDevice.find_and_modify(query={'device_id': sid}, remove=True)

    ################################################################################################################
    # Disable the given authorization for a paired device, without removing it.
    ################################################################################################################
    def revoke_authorization(self):
        self.auth_enabled = False