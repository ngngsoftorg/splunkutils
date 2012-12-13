#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.

import sys, os
import logging, logging.handlers
import http


class https(http.http):
    """ Extends http.  http handles https as well. This class is just for convenience. """