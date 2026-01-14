#!/usr/bin/env python3

# The Usual Suspects
# import keyser_soze
import os, sys, io, platform
import shutil, subprocess, getpass
import random
import math

# For some decorator action
import functools

# Reg Exprs... I have the POWER!!!!!!!!!
import re

# For Viewing Stoof
import pydoc

# For Shell Stoof
import shutil

# For Hasing
import hashlib

# More Hashing and Zipping/Unzipping
import zlib, gzip

# Random Stuff
import random

# Date/Timestamp Stuff
import datetime as datetime_mod
import time
from datetime import datetime, timedelta, timezone

# When things go wrong....oh.... so wrong...
import inspect, traceback, logging

# Because the world is the web and json at this point
import requests, json

# Because I am both argumentative and love to parse things (I am lazy WCIS)
import argparse, configparser

# CSV Is not Mad DB Skill's Y'All.... but still useful for simple sh*t
import csv

# For UUID, Guid
import uuid

# Importing/Reflection/Plugins
import importlib, importlib.util

# Because IP aren't easy to deal with
import ipaddress

# For User ID
import getpass

# URL/Web Stuff
import urllib3, requests

#
# Philosophy
#
# Nobody's perfect, this means YOU too. Best not to require anyone else be perfect or
# eventually you will be held to that same standard. Forgiveness IS divine.
#
# Blind punishment without wisdom is far worse then no punishment at all.
#

#
# Motto : I am efficient, merely because I am lazy, that is why this py_module exists
#

#
# Goals : To add some simple functionality without having to PIP overly complicated stuff
#

#
# Helper Classes
#

# ItemID Base Class
class ItemID:
	"""Base class for objects that need an ID of some kind"""

	# ID for object
	ID = None

	# Initialize Incident
	def __init__(self,id=None,min_id=0,max_id=99999):
		"""Initialize Instance"""

		if id == None:
			self.RandomID(min_id,max_id)
		else:
			self.SetID(id)

	# Set ID
	def SetID(self,id):
		"""Set ID"""

		self.ID = id

	# Set A Random Integer ID
	def RandomID(self,min_id=0,max_id=99999):
		"""Set a Random Integer Number"""

		self.SetID(random.randint(min_id,max_id))

# Unique ID Class (Guid)
class UniqueID(ItemID):
	"""Base class for GUID Unique IDs for Instances"""

	# Init Instance
	def __init__(self,id=None):
		"""Init Instance"""

		super().__init__()

		if id != None and type(id) != uuid.UUID:
			if type(id) == int:
				id = uuid.UUID(int=id)
			else:
				id = None

		self.SetID(id)

	# Set ID
	def SetID(self,id):
		"""Set UUID"""

		if id == None or type(id) != uuid.UUID:
			self.RandomID()
		else:
			self.ID = id

	# Set Random UUID
	def RandomID(self,min_id=None,max_id=None):
		"""Set Random UUID, min/max_id ignored"""

		self.SetID(uuid.uuid4())

# Taggable Base Class
class Taggable:
	"""
	Subclass to simulate the Tag feature of Visual Basic.
	The intent is provide and derived class with a generic place
	to store anything. Becareful to be sure your code can recognize
	the data types stored there and always check for None
	"""
	Tag = None

	# Init Taggable Instance
	def __init__(self,tag=None):
		self.Tag = tag

# ItemProcessor Class
class ItemProcessor(UniqueID, Taggable):
	"""Item Processor

	Processing Function is of the form...

	def Processor(item,data):

	Where 'item' is item to be processed and 'data' is an optional
	data structure meaningful to this processor... or not.

	If the processor does not use extra data structures, then this
	can be ignored.
	"""

	def __init__(self, name, processor, tag=None):
		"""Init Instance"""

		UniqueID.__init__(self)
		Taggable.__init__(self,tag)

		self.Name = name
		self.Processor = processor

	def Process(self, item, data=None):
		"""Use Processing Function to Process a Buffer"""

		return self.processor(item,data)

class ItemProcessingPipeline(UniqueID, Taggable):
	"""Item Processing Pipeline Helper"""

	def __init__(self, processor=None, name=None, tag=None):
		"""Init Instance"""

		UniqueID.__init__(self)
		Taggable.__init__(self,tag)

		self.Pipeline = list()

		item = None

		if processor:
			if type(processor) == ItemProcessor:
				item = processor
			else:
				item = ItemProcessor(name,processor)

			self.Pipeline.append(item)

	def Add(self, processor, name=None):
		"""Add Pipeline Processor"""

		item = None

		if type(processor) == ItemProcessor:
			item = processor
		else:
			item = ItemProcessor(name,processor)

		self.Pipeline.append(item)

	def Process(self, item, data=None):
		"""Process Item With Pipeline"""

		result = item

		for p in self.Pipeline:
			result = p.Processor(result,data)

		return result

#
# Stack and Queue are not good for performance.
# I recommend you use something else if you need performance
#

# Stack Class
class Stack(Taggable):
	"""A Simple Stack Class"""

	__stack__ = None

	# Init Instance
	def __init__(self):
		"""Init instance"""

		super().__init__()

		self.__stack__ = list()

	# Push Item On To Stack
	def push(self,item):
		"""Push Item Onto Stack"""

		self.__stack__.append(item)

	# Push a list
	def pushall(self,items):
		"""Push All Items Onto Stack, if Items is a List"""

		if type(items) is list:
			self.__stack__.extend(items)
		else:
			self.push(items)

	# Pop Item From Stack
	def pop(self,count=1):
		"""Pop Item Off Stack"""

		item = None

		if count == 1:
			item = self.__stack__.pop()
		elif count > 1 and count < self.len():
			rcount = count * -1

			item = self.__stack__[rcount:]

			self.__stack__ = self.__stack__[0:count]

		return item

	# Peek At Top of Stack
	def peek(self):
		"""Peek At Top Of Stack"""

		item = None

		if len(self.__stack__) > 0:
			item = self.__stack__[-1]

		return item

	# Length of Stack
	def len(self):
		"""Size of Current Stack"""

		return len(self.__stack__)

	# Get Entire Stack as List
	def getstack(self):
		"""Return Stack, as List"""

		return self.__stack__

# Queue Class
class Queue(Taggable):
	"""A Simple Stack Class"""

	__queue__ = None

	# Init Instance
	def __init__(self):
		"""Init instance"""

		super().__init__()

		self.__queue__ = list()

	# Enqueue
	def enqueue(self,item):
		"""Enqueue Item"""

		self.__queue__.append(item)

	# Enqueue all items in a supplied list
	def enqueueall(self,items):
		"""Enqueue all Items From List"""

		if type(items) is list:
			self.__queue__.extend(items)
		else:
			self.enqueue(items)

	# Dequeue Item
	def dequeue(self,count=1):
		"""Dequeue"""

		first_in = None

		length = self.len()

		if length > 0 and (count > 0 and count < length):
			if count == 1:
				first_in = self.__queue__[0]

				if length == 1:
					self.__queue__.pop()
				else:
					self.__queue__ = self.__queue__[1:]
			else:
				first_in = self.__queue__[0:count]

				self.__queue__ = self.__queue__[count:]

		return first_in

	# Peek At Top of Stack
	def peek(self,index=-1):
		"""Peek At Point In Queue"""

		item = None

		if index <= 0:
			item = self.__queue__[0]
		elif index < self.len():
			item = self.__queue__[index]

		return item

	# Length of Stack
	def len(self):
		"""Length of current queue"""

		return len(self.__queue__)

	# Get Entire Queue as List
	def getqueue(self):
		"""Return Queue, as List"""

		return self.__queue__

# File System Mount Helper Class
class MountHelper(Taggable):
	"""File System Mount Helper Class"""

	"""Mount Path"""
	Path = None

	# Init Instance
	def __init__(self,path=None):
		"""Init instance"""

		super().__init__()

		self.Path = path

	# Execute Mount Command
	def __ExecuteCmd__(self,cmd,ignore,sudome=False):
		"""Execute Mount Command"""

		success = True

		# Part of Security Check, Don't Remove, not redundant
		path_str = str(self.Path)

		if not ignore and self.Mounted():
			return success
		elif cmd in [ "mount", "umount" ] and not ";" in path_str:
			# Path check here for ";" is a bit lame, attackers can use multiple encoding types to get around this
			# Have to fix this at some point, "str" should remove some of these techniques

			cmdline = None

			if sudome:
				cmdline = [ "sudo", cmd, path_str ]
			else:
				cmdline = [ cmd, path_str ]

			process = subprocess.Popen(cmdline,stdout=subprocess.PIPE)

			while True:
				output = process.stdout.readline()

				return_code = process.poll()

				if return_code != None:
					success = (return_code == 0)
					break

		return success

	# Determine If Mounted
	def Mounted(self):
		"""Determine if Path Is Mounted"""

		mounted = os.path.ismount(self.Path) if self.Path != None else False

		return mounted

	# Attempt to Mount Path (Must Have Perms)
	def Mount(self,ignore=False,sudome=False):
		"""Attempt to Mount Path"""

		return self.__ExecuteCmd__("mount",ignore,sudome)

	# Attempt to Unmount Path (Must Have Perms)
	def Unmount(self,ignore=False,sudome=False):
		"""Attempt to Unmount Path"""

		return self.__ExecuteCmd__("umount",ignore,sudome)

	# Shortcut
	def Umount(self,ignore=False,sudome=False):
		"""Short cut for Die-Hard Unix People"""

		return self.Unmount(ignore,sudome)

# DateTime Range Class
class DateTimeRange:
	"""
	This class stores a being and end date, a DateTime Range essentially along with some
	utility functions for comparisons and timedelta fun.
	"""
	Start = None
	End = None

	# Init Instance
	def __init__(self,start,end):
		self.Start = start
		self.End = end

	# Equality Operator
	def __eq__(self,obj):
		flag = False

		if obj == None:
			flag = False
		elif id(self) == id(obj):
			flag = True
		elif self.Start == ob.Start and self.End == obj.End:
			flag = True

		return flag

	# Not Equality Operator
	def __ne__(self,obj):
		return (not self == obj)

	# Get Time Delta
	def Duration(self):
		"""Return the ranges timedelta"""
		return (self.End - self.Start)

	# Determine if a datetime (or another DateTimeRange) is within this datetimerange
	def Contains(self,value):
		"""Determine if a supplied datetime/DateTimeRange is within this range"""

		flag = False

		if value is datetime:
			flag = (value >= self.Start and value <= self.End)
		elif value is DateTimeRange:
			flag = (value.Start >= self.Start and value.End <= self.End)

		return flag

	# Determine if a DateTimeRange overlaps this one
	def Overlaps(self,value):
		"""
		Determine if supplied DateTimeRange overlaps this one.
		A tuple is returned, the first value is the truth value, True or False.
		The second value is represents how the given range overlaps the current one.
		-1 means the supplied range overlaps the Start datetime, 0 means they are
		exactly the same and 1 means the supplied range overlaps the End datetime.
		If the given range contains the current range, the second value will be 2.
		If the supplied ranges does not overlap the current one, False is returned
		and the second value is undefined.
		"""

		overhow = None
		overlap = False

		if self == value:
			# overlaps exactly
			overhow = 0
			overlap = True
		elif value.Start < self.Start and value.End >= self.Start and value.End <= self.End:
			# Overlaps Start
			overhow = -1
			overlap = True
		elif value.End > self.End and value.Start >= self.Start:
			# Overlaps End
			overhow = 1
			overlap = True
		elif value.Start < self.Start and value.End > self.End:
			# Value contains current range
			overhow = 2
			overlap = True

		return (overlap,overhow)

# Search Helper Subclass
class TimestampConverter(Taggable):
	"""Convience Class for working Date/Time Strings"""

	# Time formats
	# [key = re of string format] = [value = strptime fmt string]
	__time_formats__ = { r"^\d{4}/\d{1,2}/\d{1,2}$" : r"%Y/%m/%d",
			r"^\d{4}\d{2}\d{2}$" : r"%Y%m%d",
			r"^\d{4}\d{2}\d{2}\s+\d{2}:\d{2}$" : r"%Y%m%d %H:%M",
			r"^\d{4}\d{2}\d{2}\+ \d{2}:\d{2}:\d{2}$" : r"%Y%m%d %H:%M:%S",
			r"^\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}\:\d{1,2}\:\d{1,2}$" : r"%Y/%m/%d %H:%M:%S",
			r"^\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}\:\d{1,2}\:\d{1,2}\s+([aA]|[pP])[mM]$" : r"%Y/%m/%d %H:%M:%S %p",
			r"^\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}\:\d{1,2}$" : r"%Y/%m/%d %H:%M",
			r"^\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}\:\d{1,2}\s+([aA]|[pP])[mM]$" : r"%Y/%m/%d %H:%M %p",
			r"^\d{1,2}/\d{1,2}/\d{1,2}$" : r"%y/%m/%d",
			r"^\d{1,2}/\d{1,2}/\d{1,2}\s+\d{1,2}\:\d{1,2}\:\d{1,2}$" : r"%y/%m/%d %H:%M:%S",
			r"^\d{1,2}/\d{1,2}/\d{1,2}\s+\d{1,2}\:\d{1,2}\:\d{1,2}\s+([aA]|[pP])[mM]$" : r"%y/%m/%d %H:%M:%S %p",
			r"^\d{1,2}/\d{1,2}/\d{1,2}\s+\d{1,2}\:\d{1,2}$" : r"%y/%m/%d %H:%M",
			r"^\d{1,2}/\d{1,2}/\d{1,2}\s+\d{1,2}\:\d{1,2}\s+([aA]|[pP])[mM]$" : r"%y/%m/%d %H:%M %p",
			r"^\d{1,2}/\d{1,2}/\d{4}$" : r"%m/%d/%Y",
			r"^\d{1,2}/\d{1,2}/\d{4}$\s+\d{1,2}\:\d{1,2}$" : r"%m/%d/%Y %H:%M",
			r"^\d{1,2}/\d{1,2}/\d{4}$\+\d{1,2}\:\d{1,2}\:\d{1,2}$" : r"%m/%d/%Y %H:%M:%S",
			r"^\d{1,2}/\d{1,2}/\d{4}$\s+\d{1,2}\:\d{1,2}\s+([aA]|[pP])[mM]$" : r"%m/%d/%Y %H:%M %p",
			r"^\d{1,2}/\d{1,2}/\d{4}$\+\d{1,2}\:\d{1,2}\:\d{1,2}$" : r"%m/%d/%Y %H:%M:%S",
			r"^\d{1,2}/\d{1,2}/\d{4}$\+\d{1,2}\:\d{1,2}\:\d{1,2}\s+([aA]|[pP])[mM]$" : r"%m/%d/%Y %H:%M:%S %p",
			r"^\w+\s+\d{1,2}\s+\d{4}$" : r"%b %d %Y",
			r"^\w+\s+\d{1,2}\s+\d{4}\s+\d{1,2}:\d{1,2}$" : r"%b %d %Y %H:%M",
			r"^\w+\s+\d{1,2}\s+\d{4}\s+\d{1,2}:\d{1,2}\s+([aA]|[pP])[mM]$" : r"%b %d %Y %H:%M %p",
			r"^\w+\s+\d{1,2}\s+\d{4}\s+\d{1,2}:\d{1,2}:\d{1,2}$" : r"%b %d %Y %H:%M:%S",
			r"^\w+\s+\d{1,2}\s+\d{4}\s+\d{1,2}:\d{1,2}:\d{1,2}\s+([aA]|[pP])[mM]$" : r"%b %d %Y %H:%M:%S %p",
			r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}$" : r"%Y-%m-%d %H:%M:%S",
			r"^\d{1,2}/\d{1,2}/\d{4}$\s+ \d{1,2}\:\d{1,2}\:\d{1,2}\s+([aA]|[pP])[mM]$" : r"%m/%d/%Y %H:%M:%S %p",
		}

	# Shortcut map
	__ShortcutHandlers__ = {
		"today" : None,
		"lasthour" : None,
		"yesterday" : None,
		"weekago" : None,
		"lastweek" : None,
		"fortniteago" : None,
		"monthago" : None,
		"lastmonth" : None,
		"yearago" : None,
		"lastyear" : None,
		"last24" : None,
		"last48" : None,
		"last72" : None,
		"last24hours" : None,
		"last48hours" : None,
		"last72hours" : None,
                "lastday": None,
		"last2days" : None,
		"last3days" : None,
		"last4days" : None,
		"last5days" : None,
		"last10days" : None
	}

	__DeltaShortcutHandlers__ = {
		"microseconds" : [ r"^(?P<count>\d+)mic(ro|rosec|roseconds){0,1}$", None, "Microseconds"],
		"milliseconds" : [ r"^(?P<count>\d+)(ms|milliseconds){0,1}$", None, "Milliseconds" ],
		"second" : [ r"^second$", None, "1 second" ],
		"seconds" : [ r"^(?P<count>\d+)s(econd|econds){0,1}$", None, "Seconds" ],
		"minute" : [ r"^m(min|minute){0,1}$", None, "1 minute"],
		"minutes" : [ r"^(?P<count>\d+)m(inute|inutes){0,1}$", None, "minutes" ],
		"hour" : [ r"^h(our){0,1}$", None, "1 Hour" ],
		"hours" : [ r"^(?P<count>\d+)h(our|ours){0,1}$", None, "Hours" ],
		"last24" : [ r"^last(?P<count>\d+)$", None, "Last 24 Hours" ],
		"last48" : [ r"^last(?P<count>\d+)$", None, "Last 48 Hours" ],
		"last72" : [ r"^last(?P<count>\d+)$", None, "Last 72 Hours" ],
		"day" : [ r"^d(ay){0,1}$", None, "One day, 24 hours" ],
		"days" : [ r"^(?P<count>\d+)d(ay|ays|s){0,1}$", None, "Days" ],
		"week" : [ r"^w(eek){0,1}$", None, "1 Week, 7 days" ],
		"weekago" : [ r"^weekago$", None, "One 7 day interval" ],
		"weeks" : [ r"^(?P<count>\d+)w(eek|eeks|s){0,1}$", None, "7 day intervals" ],
		"month" : [ r"^mon(th){0,1}$", None, "30 day interval" ],
		"months" : [ r"^(?P<count>\d+)(M|mon){1}(onth|onths|th|ths){0,1}$", None, "30 day intervals, not accurate, I know" ],
		"year" : [ r"^y(ear){0,1}$", None, "One year, 365 days" ],
		"years" : [ r"^(?P<count>\d+)y(ear|ears){0,1}$", None, "Year intervals" ],
		"decade" : [ r"^decade$", None, "One decade, 10 years"],
		"decades" : [ r"^(?P<count>\d+)dec(ade|ades){0,1}$", None, "Decade intervals" ],
		"century" : [ r"^century$", None, "One century, 100 years" ],
		"centuries" : [ r"^(?P<count>\d+)cen(tury|turies){0,1}$", None, "Century intervals"],
		"millenia" : [ r"^(?P<count>\d+)mil(lenia){0,1}$", None, "1000 year intervals" ]
	}

	# Short Cut Callbacks
	Shortcuts = None

	# Time Delta Shortcuts
	DeltaShortcuts = None

	# Last Converted Timestamp
	Converted = None

	# Init Shortcuts
	def __init__(self,timestamp_str = None):
		"""Init instance"""

		super().__init__()

		self.Shortcuts = dict(self.__ShortcutHandlers__)
		self.DeltaShortcuts = dict(self.__DeltaShortcutHandlers__)

		self.__FillMaps__()

		if timestamp_str != None:
			self.ConvertTimestamp(timestamp_str)

	# Print Conversion map and shortcuts
	def Print(self,output=True):
		"""Print Filters and Shortcuts"""

		msg = CombiBar("Shortcuts") + "\n"

		for shortcut in self.__ShortcutHandlers__.keys():
			msg += f"{shortcut}\n"

		msg += ("\n" + CombiBar("Time Delta Shortcuts") + "\n")

		for name,list in self.__DeltaShortcutHandles__.keys():
			pattern,func,comment = list

			msg += f"{name:<20}\t{pattern:<25}\t{comment}\n"

		msg += ("\n" + CombiBar("Conversion Formats") + "\n")

		for reg,tsf in self.__time_formats__.items():
			msg += f"{tsf:<20}\t{reg}\n"

		if output:
			Msg(msg)

		return msg

	# Convert 'today' shortcut to a timestamp
	def Today(self):
		"""Converts a 'today' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow().date()
		value = datetime(today.year,today.month,today.day, tzinfo=timezone.utc)

		return value

	# Convert 'yesterday' shortcut to a timestamp
	def Yesterday(self):
		"""Converts a 'yesterday' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(days=1)
		value = datetime(today.year,today.month,today.day, tzinfo=timezone.utc)

		return value

	# Convert 'weekago' shortcut to a timestamp
	def WeekAgo(self):
		"""Converts a 'weekago' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(weeks=1)
		value = datetime(today.year,today.month,today.day, tzinfo=timezone.utc)

		return value

	# Convert 'fortniteago' shortcut to a timestamp
	def FortniteAgo(self):
		"""Converts a 'fortniteago' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(weeks=2)
		value = datetime(today.year,today.month,today.day, tzinfo=timezone.utc)

		return value

	# Convert 'monthago' shortcut to a timestamp (this cheats by value on the first day of the previous month)
	def MonthAgo(self):
		"""Converts a 'monthago' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow()

		lastmonth = datetime(today.year,today.month,1) - timedelta(days=1)

		value = datetime(lastmonth.year,lastmonth.month,1, tzinfo=timezone.utc)

		return value

	# Convert 'lastmonth' shortcut
	def LastMonth(self):
		"""Converts a 'lastmonth' temporal shortcuts in a date field into a DateTime object"""

		return self.MonthAgo()

	# Convert 'yearago' shortcut to a timestamp
	def YearAgo(self):
		"""Converts a 'yearago' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(weeks=52)
		value = datetime(today.year,today.month,today.day, tzinfo=timezone.utc)

		return value

	# Convert 'lastyear' shortcut to a timestamp
	def LastYear(self):
		"""Converts a 'lastyear' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow()

		value = datetime(today.year - 1,1,1, tzinfo=timezone.utc)

		return value

	# Convert 'last24' shortcut into a timestamp
	def Last24(self):
		"""Converts a 'last24' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(hours=24)

		value = datetime(today.year,today.month,today.day,today.hour,today.minute,today.second,tzinfo=timezone.utc)

		return value

	# Convert 'last48' shortcut into a timetamp
	def Last48(self):
		"""Converts a 'last48' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(hours=48)

		value = datetime(today.year,today.month,today.day,today.hour,today.minute,today.second,tzinfo=timezone.utc)

		return value

	# Convert 'last72' shortcut into a timestamp
	def Last72(self):
		"""Converts a 'last72' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(hours=72)

		value = datetime(today.year,today.month,today.day,today.hour,today.minute,today.second,tzinfo=timezone.utc)

		return value

	# Convert 'lasthour' shortcut into timestamp
	def LastHour(self):
		"""Converts a 'lasthour' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(hours=1)

		value = datetime(today.year,today.month,today.day,today.hour,tzinfo=timezone.utc)

		return value

	# Convert 'last2days' shortcut into timestamp
	def Last2Days(self):
		"""Converts a 'last2days' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(days=2)

		value = datetime(today.year,today.month,today.day,tzinfo=timezone.utc)

		return value

	# Convert 'last3days' shortcut into timestamp
	def Last3Days(self):
		"""Converts a 'last3days' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(days=3)

		value = datetime(today.year,today.month,today.day,tzinfo=timezone.utc)

		return value

	# Convert 'last4days' shortcut into timestamp
	def Last4Days(self):
		"""Converts a 'last4days' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(days=4)

		value = datetime(today.year,today.month,today.day,tzinfo=timezone.utc)

		return value

	# Convert 'last5days' shortcut into timestamp
	def Last5Days(self):
		"""Converts a 'last5days' temporal shortcuts in a date field into a DateTime object"""

		today = datetime.utcnow() - timedelta(days=5)

		value = datetime(today.year,today.month,today.day,tzinfo=timezone.utc)

		return value

	# Convert 'last10days' shortcut into timestamp
	def Last10Days(self):
		"""Converts a 'last10days' temporal shortcuts in a date field into a DateTime"""

		today = datetime.utcnow() - timedelta(days=10)

		value = datetime(today.year,today.month,today.day,tzinfo=timezone.utc)

		return value

	# Replace Temporal Shortcuts in value field
	def ReplaceShortcuts(self,value,zone=None):
		"""Replace temporal shortcuts function"""

		mapped_func = self.Shortcuts.get(value,None)

		if mapped_func:
			value = mapped_func()
		else:
			pass

		return value

	def DeltaMicroseconds(self,count):
		"""Microseconds Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(microseconds=count)

		return delta

	def DeltaMilliseconds(self,count):
		"""Millisecond Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(milliseconds=count)

		return delta

	def DeltaSeconds(self,count):
		"""Seconds Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(seconds=count)

		return delta

	def DeltaMinutes(self,count):
		"""Minutes Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(minutes=count)

		return delta

	def DeltaHours(self,count):
		"""Hours Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(hours=count)

		return delta

	def DeltaLastHoursX(self,count):
		"""LastHour X Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(hours=count)

		return delta

	def DeltaDays(self,count):
		"""Days Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(days=count)

		return delta

	def DeltaWeeks(self,count):
		"""Weeks Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(weeks=count)

		return delta

	def DeltaMonths(self,count):
		"""Months Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(days=(count*30))

		return delta

	def DeltaYears(self,count):
		"""Years Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(days=(count*365))

		return delta

	def DeltaDecades(self,count):
		"""Decades Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(days=((365*10)*count))

		return delta

	def DeltaCenturies(self,count):
		"""Centuries Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(days=(((365*10)*100)*count))

		return delta
	def DeltaMillenia(self,count):
		""" Delta Handler"""

		delta = None

		if count is not None:
			delta = timedelta(days=(((365*10)*1000)*count))

		return delta

	def GetDelta(self,data):
		"""Delta Handler Finder"""

		entry = None
		pattern = None
		func = None
		comment = None
		delta = None

		if data in self.DeltaShortcuts:
			pattern, func, comment = self.DeltaShortcuts[data]

			match = re.search(pattern,data)

			if match is not None:
				count = 1

				if "count" in match.groupdict().keys():
					count = int(match.group("count"))

				delta = func(count)
			else:
				delta = func(1)
		else:
			for entry in self.DeltaShortcuts.items():
				name,value = entry
				pattern, func, comment = value

				match = None

				try:
					match = re.search(pattern,data)
				except Exception as err:
					ErrMsg(err,f"Pattern, {pattern} caused an error")

				if match is not None:
					count = 1

					if "count" in match.groupdict().keys():
						count = int(match.group("count"))

					delta = func(count)

					break

		return delta

	# Convert a string Timestamp (or shortcut) into a datetime TimeStamp
	def ConvertTimestamp(self,timestamp_str,zone=None):
		"""Convert String timestamp to DateTime"""

		key = None
		parse_fmt = None
		value = None

		if type(timestamp_str) is str:
			for key,fmt in self.__time_formats__.items():
				if re.search(key,timestamp_str):
					parse_fmt = fmt
					break

			if not parse_fmt is None:
				ts = datetime.strptime(timestamp_str,parse_fmt)

				value = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, tzinfo=zone)
			else:
				shortcut_keys = [ key for key in self.Shortcuts.keys() ]

				tss = timestamp_str.lower()

				if tss in shortcut_keys:
					value = self.ReplaceShortcuts(tss,zone=zone)

		return value

	# Convert Epoch Value to DateTime
	def FromEpoch(self,timestamp,divider=1):
		"""Convert an Epoch Time (of some kind) to  DateTime"""

		if divider > 1:
			timestamp /= divider

		new_timestamp = datetime.fromtimestamp(timestamp)

		return new_timestamp

	# Convert to Epoch Time
	def ToEpoch(self,timestamp,multiplier=1):
		"""Convert Timestamp string to Epoch Time"""

		value = 0

		if type(timestamp) is str:
			value = self.ConvertTimestamp(timestamp)
			value = int(value.timestamp()) * multiplier
		elif type(timestamp) is datetime:
			value = timestamp.timestamp() * multiplier

		return value

	# Convert to Epoch Milliseconds
	def ToEpochMilliseconds(self,timestamp):
		"""Convert timestamp string to Epoch Time in Milliseconds"""

		value = self.ToEpoch(timestamp,multiplier=1000)

		return value

	# Add/Replce Shortcut to shortcut table
	def AddShortcut(self,shortcut,func):
		"""Add/Replace a function to the shortcut table"""

		self.Shortcuts[shortcut] = func

	# Add Delta Shortcut
	def AddDelta(self,name,func):
		"""Add/Replace a function to the Delta Shortcuts table"""

		self.DeltaShortcuts[name][1] = func

	# Add Time Format Extractor
	def AddTimeFormat(self,reg_exp,formatter):
		"""Add Time Format Extractor"""

		self.__time_formats__[reg_exp] = formatter

	# Check Shortcut Strings
	def InShortcuts(self,pattern):
		"""Check to see if supplied string is in Shortcuts"""

		if pattern.lower() in self.Shortcuts.keys():
			return True

		return False

	def InDeltas(self,pattern):
		"""Check to see if supplied string is in Delta Shortcuts"""

		flag = False

		if pattern.lower() in self.DeltaShortcuts.keys():
			return not flag

		for sc in self.DeltaShortcuts.keys():
			entry = self.DeltaShortcuts[sc]

			rep,func,comment = entry

			if re.search(rep,pattern) is not None:
				flag = True
				break

		return flag

	# Fill in Maps
	def __FillMaps__(self):
		"""Fill shortcut map (router map) with shortcut replacement functions"""

		# Time Shortcuts
		self.AddShortcut("today",self.Today)
		self.AddShortcut("lasthour",self.LastHour)
		self.AddShortcut("yesterday",self.Yesterday)
		self.AddShortcut("weekago",self.WeekAgo)
		self.AddShortcut("lastweek",self.WeekAgo)
		self.AddShortcut("fortniteago",self.FortniteAgo)
		self.AddShortcut("monthago",self.MonthAgo)
		self.AddShortcut("lastmonth",self.LastMonth)
		self.AddShortcut("yearago",self.YearAgo)
		self.AddShortcut("lastyear",self.LastYear)
		self.AddShortcut("last24",self.Last24)
		self.AddShortcut("last48",self.Last48)
		self.AddShortcut("last72",self.Last72)
		self.AddShortcut("last24hours",self.Last24)
		self.AddShortcut("last48hours",self.Last48)
		self.AddShortcut("last72hours",self.Last72)
		self.AddShortcut("lastday",self.Last24)
		self.AddShortcut("last2days",self.Last2Days)
		self.AddShortcut("last3days",self.Last3Days)
		self.AddShortcut("last4days",self.Last4Days)
		self.AddShortcut("last5days",self.Last5Days)
		self.AddShortcut("last10days",self.Last10Days)

		# Time Delta Shortcuts
		self.AddDelta("microseconds",self.DeltaMicroseconds)
		self.AddDelta("milliseconds",self.DeltaMilliseconds)
		self.AddDelta("seconds",self.DeltaSeconds)
		self.AddDelta("seconds",self.DeltaSeconds)
		self.AddDelta("minute",self.DeltaMinutes)
		self.AddDelta("minutes",self.DeltaMinutes)
		self.AddDelta("hour",self.DeltaHours)
		self.AddDelta("hours",self.DeltaHours)
		self.AddDelta("last24",self.DeltaLastHoursX)
		self.AddDelta("last48",self.DeltaLastHoursX)
		self.AddDelta("last72",self.DeltaLastHoursX)
		self.AddDelta("day",self.DeltaDays)
		self.AddDelta("days",self.DeltaDays)
		self.AddDelta("week",self.DeltaWeeks)
		self.AddDelta("weekago",self.DeltaWeeks)
		self.AddDelta("weeks",self.DeltaWeeks)
		self.AddDelta("month",self.DeltaMonths)
		self.AddDelta("months",self.DeltaMonths)
		self.AddDelta("year",self.DeltaYears)
		self.AddDelta("years",self.DeltaYears)
		self.AddDelta("decade",self.DeltaDecades)
		self.AddDelta("decades",self.DeltaDecades)
		self.AddDelta("century",self.DeltaCenturies)
		self.AddDelta("centuries",self.DeltaCenturies)
		self.AddDelta("millenia",self.DeltaMillenia)

# Rate Limiter Class
class RateLimiter:
	"""
	Used to help regular the number of times a sequence of commands can be used in a given interval.
	"""

	times_per_interval = 1
	interval = timedelta(seconds=1)
	sleepfor = 0.25
	gap = None

	interval_start = None
	next_interval = None
	run_count = 0

	# Init Rate Limiter
	def __init__(self,times_per_interval,interval,sleepfor=None,gap=None):
		"""
		Init instance of RateLimiter

		If interval is not a timedelta, then it is assumed to be seconds and
		converted to a timedelta object for that many seconds.
		"""
		self.times_per_interval = times_per_interval

		if type(interval) == int:
			interval = timedelta(seconds=interval)

		self.interval = interval

		if sleepfor != None:
			self.sleepfor = sleepfor

		if gap != None:
			self.gap = gap

	# Check Function
	def Check(self):
		"""
		Checks the current rate and limits if need be
		"""

		if self.interval_start == None: self.interval_start = datetime.now()

		self.next_interval = self.interval_start + self.interval

		if self.run_count >= self.times_per_interval and datetime.now() < self.next_interval:
			self.run_count = 0

			while datetime.now() < self.next_interval:
				time.sleep(self.sleepfor)

			self.interval_start = datetime.now()

		if self.gap != None:
			time.sleep(self.gap)

		self.run_count += 1

	# Generate a sleep Gap Based on the number of known iterations
	def AutoGap(self,iterations):
		if iterations > self.times_per_interval:
			iterations_per_interval = self.interval.total_seconds() / self.times_per_interval
			self.gap = iterations / iterations_per_interval

		return self.gap

class TraceComment(Taggable):
	"""Line Trace Comment"""

	line = -1
	comment = ""
	timestamp = datetime.min

	def __init__(self, line=-1, comment=""):
		"""Init Instance"""

		self.line = line
		self.comment = comment
		self.timestamp = datetime.now()

	def Print(self):
		"""Pretty Print Instance"""

		Msg(f"Line\t: {self.line}")
		Msg(f"Comment\t: {self.comment}")
		Msg(f"Time\t: {self.timestamp}")

class DbgLineTracer(Taggable):
	"""Line Tracer for Debugging"""

	comments = None

	def __init__(self):
		"""Init Instance"""

		self.comments = list()


	def Add(self,line,comment=""):
		"""Add A Line Trace Comment"""

		objcomment = TraceComment(line,comment)

		self.comments.append(objcomment)

	def Clear(self):
		"""Clear Comments"""

		self.comments.clear()

	def Last(self):
		"""Get Last Entered Comment"""

		return self.comments[-1]


#
# Module Variables and Constants
#

# Version (Mine, and PEP defactos)
VERSION=(0,0,57)
Version = __version__ = ".".join([ str(x) for x in VERSION ])

# Start Random Generator
random.seed()

# Begin Debug Mode Items

# Signals Debug mode operations
__DebugMode__ = False

# Profiler Dict item[blk_name] = (average_time, count_called)
Profiler = dict()

# Debug/Breakpoint Flags
DebugLabels = None		# Dictionary of labels, not enabled is None
DebugLabelExists = False	# If False, NONE (no label) and non-explicitly defined labels are all enabled by default

# Some exceptional labels (i.e. printed even when DebugMode() == False, even though they still have to be enabled)

# Informational Debug Messages
Informational = "informational"

# List of exceptions (Uses can add to these during run time)
LabelExceptions = [  Informational ]

# Exceptions will not bre processed unless enabled first
LabelExceptionsEnabled = False

# List of BreakOn Labels
BreakOnLabel = list()

# List of BreakOn Conditions
BreakWhenConditions = dict()

# List of Events Reported
EventLists = dict()
EventLists["default"] = list()
CurrentEventList = "default"

# End DebugMode Items

# Signals Module is being used in Cmd Line Mode
__CmdLineMode__ = False

# Notes:
# DebugMode puts the module in DebugMode, i.e. it activates DbgMsg() to output
# 	when DebugMode is false, DbgMsg does nothing.
# CmdLineMode informs the module that it should behave like it was called as a script.
# 	when CmdLineMode is false, it assumes it is in ModuleMode and will refrain, as best
#	possible to not do anything CmdLine like (i.e. print to stdout).
#
# These can be used by the calling scripts or modules to alter behavior. Also note the
# function ModuleMode, merely inverts the CmdLineMode flag, there are the same indicator,
# just different expressions of it.
# The Msg and DbgMsg functions allow for providing an external function that will recieve
# the supplied message or arguments. The function will define where the message goes,
# internal logging mechanisms, system logs, etc. That is its purpose.
#

# IP Expresions
IPv4_Exp = r"(\d{1,3}\.){3}\d{1,3}"
IPv4_Exp_ABS = r"^{}$".format(IPv4_Exp)
NETIPv4_Exp = r"^{}/\d+$".format(IPv4_Exp)

IPv6_Exp = r"([\dabcdef]{1,4}:){1,7}:[\dabcdef]{0,4}"
IPv6_Exp_ABS = r"^{}$".format(IPv6_Exp)
NETIPv6_Exp = r"^{}/\d+$".format(IPv6_Exp)

# Log File
Logfile = r"C:\WINDOWS\TEMP\run.log" if sys.platform == "win32" else f"/tmp/run.log.{getpass.getuser()}"

# Tee File
Teefile = None

#
# Lambdas
#

# Enqueue Item 'x' in Queue 'L' (Which is really a list)
Enqueue = lambda L,x : L.append(x)
# Dequeue Item from Queue 'L' (Which is really a list)
Dequeue = lambda L : L.pop(0)
# Peekqueue
Peekqueue = lambda L : L[-1]

# Push Item On Stack
Push = lambda L,item : L.append(item)
# Pop Item From Stack
Pop = lambda L : L.pop()
# Peek at Stack
Peek = lambda L : L[-1]

# Parse Text Bool Value to Actual Boolean Value
ParseBool = lambda S : False if S.lower() == "false" else True

# Get CreationTime For File As DateTime
CreationTime = lambda filename : datetime.fromtimestamp(os.path.getctime(filename))
# Get ModificationTime For File As DateTime
ModificationTime = lambda filename : datetime.fromtimestamp(os.path.getmtime(filename))
# Get AccessTime For File As DateTime
AccessTime = lambda filename : datetime.fromtimestamp(os.path.getatime(filename))

# Kewl (Stupid Diagnostic stuff)
Kewl = lambda : print("Kewl")

#
# Functions
#

#
# Debug, CmdLine and Module Mode Items
#

# Get or Set DebugMode
def DebugMode(flag=None,logfile=None):
	"""Get or Set DebugMode"""

	global __DebugMode__, Logfile

	if flag: __DebugMode__ = flag
	if logfile != None: Logfile = logfile

	return __DebugMode__

# Get or Set CmdLineMode
def CmdLineMode(flag=None):
	"""Get or set CmdLineMode, the opposite of ModuleMode"""
	global __CmdLineMode__

	if flag != None: __CmdLineMode__ = flag

	return __CmdLineMode__

# Alternative Inverse Verb for CmdLineMode
def ModuleMode(flag=None):
	"""Get or Set ModuleMode (the opposite of CmdLineMode)"""

	if flag != None: flag = not flag

	return (not CmdLineMode(flag))

#
# Controllable Messaging Functions
#

# Log Message
def Log(msg,logfile=None,timestamp=False,end="\n",includeCaller=False,callerframe=None):
	"""
	Send Message to Log
	"""

	global Logfile

	if callerframe == None: callerframe = inspect.currentframe().f_back

	if logfile == None: logfile = Logfile

	prefix = ""
	buffer = msg

	if timestamp: prefix = datetime.now()

	if includeCaller:
		module = callerframe.f_code.co_filename
		line = callerframe.f_lineno
		host = platform.node()

		caller_str = f"{host}[{module}({line})]"

		buffer = f"{buffer} {caller_str}"

	if prefix != None:
		buffer = f"{prefix} - {msg}"

	if type(logfile) == str:
		with open(logfile,"at") as log:
			log.write(buffer + end)
	else:
		try:
			logfile.write(buffer + end)
		except Exception as err:
			# This may be in vain, but you never know if someone will see this error.
			print(f"An error occurred trying to write to log supplied as an object : {err}")

# A Centrally Controlled Messaging System
# msg : Message to print
# func : A simple function to pass the message to (optional)
# If "func" is supplied, Msg uses it for output instead of printing to stdout
def Msg(msg,func=None,timestamp=False,ignoreModuleMode=False,end="\n",file=sys.stdout,flush=True,binary=False):
	"""
	Centralize and Managed Messaging Function
	Only active in CmdLineMode (or when called by DbgMsg in DebugMode)
	"""

	global Teefile, Logfile

	if timestamp:
		msg = f"{datetime.now()} - {msg}"

	if CmdLineMode() or ignoreModuleMode:
		if func:
			func(msg)
		else:
			file = file if file != None else os.stdout

			if binary:
				buffer = f"{msg}{end}"

				file.write(buffer.encode())
			else:
				print(msg,end=end,file=file)

			if flush: file.flush()


	# Logfile/Teefile works no matter what mode module is in
	if Logfile != None:
		Log(msg,logfile=Logfile)

	if Teefile != None:
		Log(msg,logfile=Teefile)

def SetDebugLabel(dbglabel,value):
	"""Enable Debug Label"""

	global DebugLabels

	if DebugLabels is None:
		DebugLabels = dict()

	DebugLabels[dbglabel] = value

def EnableDebugLabel(dbglabel):
	"""Enable Debug Label"""

	SetDebugLabel(dbglabel,True)

def DisableDebugLabel(dbglabel):
	"""Disable Debug Label"""

	SetDebugLabel(dbglabel,False)

def DebugLabelBehavior(value=None):
	"""
	Set the default debug label behavior

	True to treat 'None' labels and labels not existing in DebugLabels dictionary as enabled
	False to only consider enabled labels in the DebugLabels dictionary.
	"""

	global DebugLabelExists

	if not value is None:
		DebugLabelExists = value

	return DebugLabelExists

def LoadDebugEnableFile(filename):
	"""Load Debug Enablement Data File"""


	"""
	File format:
	Row[0] can contain a label or a directive, directives are "default", "behavior", "mustexist"
	and must have a value of TRUE or FALSE or YES or NO

	if the directive exists, it defines IF the debug label must be defined AND TRUE in order to be printed.
	if no directive, then a debug label is only NOT printed when label is defined AND FALSE

	"""

	global DebugLabels, DebugLabelExists

	if DebugLabels is not None:
		del DebugLabels

	DebugLabels = None

	if os.path.exists(filename):
		DebugLabels = dict()

		with open(filename,"r",newline='') as csvfile:
			reader = csv.reader(csvfile)

			for row in reader:
				if row[0] in [ "default", "behavior", "mustexist" ]:
					DebugLabelExists = True if row[1] in [ "True","true","TRUE","1","yes","Yes","y","Y" ] else False
				else:
					DebugLabels[row[0]] = True if row[1] in [ "True","true","TRUE","1","Yes","yes","y","Y" ] else False

def IsDebugLabelEnabled(dbglabel):
	"""Check if Debug Label is Enabled"""

	global DebugLabels, DebugLabelExists

	enabled = not DebugLabelExists

	dbglb = dbglabel

	if DebugLabels is not None and dbglabel is not None:
		if type(dbglabel) is str and dbglabel in DebugLabels:
			enabled = DebugLabels[dbglabel]
			dbglb = dbglabel
		elif type(dbglabel) is list:
			for lbl in dbglabel:
				if lbl in DebugLabels:
					enabled = DebugLabels[lbl]

					if enabled:
						dbglb = lbl

					# only break when enabled. This allows the full list of labels to be checked. Slower, but who cares, we're
					# Debugging...
					if enabled: break

	return enabled,dbglb

def Breakpoint(dbglabel,test_flag=True):
	"""Check if Debug Label is Enabled AND We Are In DebugMode"""

	enabled,dbglb = IsDebugLabelEnabled(dbglabel)

	return (DebugMode() and enabled and test_flag)


# Eventing System
#
# Intended to allow a list of registered events to be maintained while executing through a script or section of a script
# The Eventing() decorator wraps a function and maintains an event list for only the function (and subsidiary
#

def CreateEventList(name, current=False):
	"""Create a named Event List"""

	global EventLists, CurrentEventList

	if not name in EventLists:
		EventLists[name] = list()

		if current:
			CurrentEventList = name

	return EventLists[name]

def SetCurrentEventList(name):
	"""Set Current Event List"""

	global EventLists, CurrentEventList

	if name is not None and name in EventLists:
		CurrentEventList = name
	else:
		raise KeyError(f"No such event list named {name}")

def GetCurrentEventList():
	"""Get Current EventList Name"""

	global CurrentEventList

	return CurrentEventList

def RemoveEventList(name):
	"""Remove An Event List"""

	global EventLists, CurrentEventList

	if name in EventLists and name != "default":
		del EventLists[name]

		if name == CurrentEventList:
			CurrentEventList = "default"

def Event(comment, event_list=None):
	"""Register An Event"""

	global EventLists, CurrentEventList

	if event_list is None:
		event_list = CurrentEventList

	if event_list in EventLists and comment is not None:
		if EventLists[event_list] is None:
			EventLists[event_list] = list()

		EventLists[event_list].append(comment)

def GetEvents(event_list=None):
	"""Get Event List"""

	global EventLists, CurrentEventList

	if event_list is None:
		event_list = CurrentEventList

	return EventLists[event_list]

def ClearEvents(event_list=None):
	"""Clear Event List"""

	global EventLists, CurrentEventList

	if event_list is None:
		event_list = CurrentEventList

	if event_list in EventLists:
		if EventLists[event_list] is None:
			EventLists[event_list] = list()

		EventList[event_list].clear()

def PrintEvents(event_list=None):
	"""Print Events"""

	global EventLists, CurrentEventList

	if event_list is None:
		event_list = CurrentEventList

	if event_list in EventLists:
		for message in EventLists[event_list]:
			Msg(message)


def Eventing(start_message, end_message=None, leave=False):
	"""Eventing Decorator"""

	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			dbgblk, dbglb = DbgNames(func)

			current = GetCurrentEventList()

			CreateEventList(dbgblk, True)

			Event(start_message)

			results = func(*args, **kwargs)

			Event(end_message)

			if not leave:
				RemoveEventList(dbgblk)

			SetCurrentEventList = current

			return results
		return wrapper
	return decorator

def BreakOn(labels, bypass=False):
	"""Break When Any Label Supplied Exists In Global BreakOnLabels List"""

	# This has minimal value, but has it's uses

	global BreakOnLabels

	breakme = False

	if type(labels) is str and labels in BreakOnLabels:
		breakme = True
	elif type(labels) is list:
		for item in labels:
			if item in BreakOnLabels:
				breakme = True
				break

	if not bypass and breakme:
		breakpoint()

	return breakme

def BreakWhen(conditions, **kwargs):
	"""Break When Conditions Met"""

	# conditions is a dictionary similar to kwargs.
	# When all the values match, BreakWhen returns true
	# to signal to force a breakpoint (or other action)

	conditions_met = True

	for warg in kwargs:
		if warg in conditions:
			if kwargs[warg] != conditions[warg]:
				conditions_met = False
				break
		else:
			conditions_met = False
			break

	return conditions_met

# A Centrally Controlled Debug Messaging System
# msg : Message to print
# func : A simple function to pass the message to (optional)
# If "func" is supplied, DbgMsg uses it for output instead of printing to stdout
def DbgMsg(msg,func=None,prefix="***",timestamp=False,end="\n",file=sys.stdout,flush=True,break_point=False,iftrue=None,iffalse=None,callerframe=None,interval_stamp=None,dbglabel=None):
	"""
	Messaging function that only prints when in DebugMode.
	Ignores CmdLineMode/ModuleMode.
	"""

	global __DebugMode__

	if __DebugMode__ or (dbglabel == LabelExceptions and LabelExceptionsEnabled):
		flag,dbglb = IsDebugLabelEnabled(dbglabel)

		if not flag:
			return False

		delta = None

		int_stamp = DbgMsg.__annotations__.get("interval_stamp",None)

		if int_stamp != None:
			delta = datetime.now() - int_stamp
			DbgMsg.__annotations__["interval_stamp"] = None
		elif interval_stamp != None:
			DbgMsg.__annotations__["interval_stamp"] = interval_stamp

		# iftrue is not none and false, skip this message
		if iftrue != None and iftrue != True:
			return False
		# iffalse is not none and false, skip this message
		if iffalse != None and iffalse != False:
			return False

		if callerframe == None:
			callerframe = inspect.currentframe().f_back

		module = callerframe.f_code.co_filename
		line = callerframe.f_lineno
		host = platform.node()

		caller_str = f"{host}[{module}({line})]"

		if timestamp:
			prefix = f"{prefix} {datetime.now()}"

		if delta != None:
			msg = f"{msg} - Delta from last call {delta}"

		# Just because I don't like putting null pointers into string functions... I know python None is not a null pointer, but it rubs
		# me the wrong way allowing this anyway.
		dbglbl = "None" if dbglb is None else dbglb

		adjusted = f"{prefix} {caller_str}/{dbglbl} : {msg}" if caller_str != "" else f"{prefix} : {msg}"

		Msg(adjusted,func,ignoreModuleMode=True,end=end,file=file,flush=flush)

		# If True, tells caller to break
		return break_point

	# If we are not executing the body of the DbgMsg, no breaking
	return False

# Block Enter Debug Messages
def DbgEnter(msg,dbglabel=None,func=None,prefix="-->",timestamp=False,end="\n",file=sys.stdout,flush=True,break_point=False,iftrue=None,iffalse=None,callerframe=None,interval_stamp=None):
	"""DbgMsg Helper Function Output a message when entering a code block"""

	message = f"Entering {msg}"

	if callerframe == None:
		callerframe = inspect.currentframe().f_back

	return DbgMsg(message,func=func,prefix=prefix,timestamp=timestamp,end=end,file=file,flush=flush,break_point=break_point,iftrue=iftrue,iffalse=iffalse,callerframe=callerframe,interval_stamp=interval_stamp,dbglabel=dbglabel)

# Block Exit Debug Messages
def DbgExit(msg,dbglabel=None,func=None,prefix="<--",timestamp=False,end="\n",file=sys.stdout,flush=True,break_point=False,iftrue=None,iffalse=None,callerframe=None,interval_stamp=None):
	"""DbgMsg Helper Function Output a message when exitting a code block"""

	message = f"Exitting {msg}"

	if callerframe == None:
		callerframe = inspect.currentframe().f_back

	return DbgMsg(message,func=func,prefix=prefix,timestamp=timestamp,end=end,file=file,flush=flush,break_point=break_point,iftrue=iftrue,iffalse=iffalse,callerframe=callerframe,interval_stamp=interval_stamp,dbglabel=dbglabel)

# Get Debug Names (Block, Label) Lambda
DbgNames = lambda object: [ object.__qualname__, object.__name__ ]

# DebugMe Decorator
def DebugMe(func):
	"""Debug Decorator For Enter/Exit Messages"""

	@functools.wraps(func)
	def wrapper(*args,**kwargs):
		dbgblk, dbglb = DbgNames(func)

		callerframe = inspect.currentframe().f_back

		DbgEnter(dbgblk,dbglb,callerframe=callerframe)

		results = func(*args,**kwargs)

		DbgExit(dbgblk,dbglb,callerframe=callerframe)

		return results

	return wrapper

def ProfileMe(func):
	"""Profile Function, for time"""

	@functools.wraps(func)
	def wrapper(*args,**kwargs):
		global Profiler

		dbgblk, dbglb = DbgNames(func)

		enter_stamp = datetime.now()

		results = func(*args,**kwargs)

		exit_delta = datetime.now() - enter_stamp

		if dbgblk in Profiler:
			previous_delta, count = Profiler[dbgblk]

			count += 1
			Profiler[dbgblk] = ((exit_delta + previous_delta) / 2, count)
		else:
			Profiler[dbgblk] = (exit_delta, 1)

		return results

	return wrapper

# DbgAuto Messages
def DbgAuto(msg="Auto Dbg",prefix="[* DbgAuto *]",callerframe=None,timestamp=False,end="\n",file=sys.stdout,flush=True,break_point=False,iftrue=None,iffalse=None,dbglabel=None):
	"""
	Generate an Automated DbgMsg With File-Line number and optional msg

	Generally the purpose here is generate temporary debug scaffolding messages for
	fast debugging. It is INTENDED that they will be removed once the debugging sequence
	is completed.
	"""

	if callerframe == None:
		callerframe = inspect.currentframe().f_back

	return DbgMsg(f"{msg}",prefix=prefix,timestamp=timestamp,end=end,file=file,flush=flush,break_point=break_point,iftrue=iftrue,iffalse=iffalse,callerframe=callerframe,dbglabel=dbglabel)

# Not Implemented yet Convenience Function
def NotImplementedYet(msg=None,prefix=">>>"):
	"""Not Implemented yet Convenience Function"""

	Msg("{} Not Implemented Yet : {}".format(prefix,msg) if msg != None else "{} Not Implemented Yet".format(prefix))

# Shortcuts
NotYetImplemented = NotImplementedYet
NotImplemented = NotImplementedYet

# A Centrally Controlled Exception Printing System
# err : The exception instance generated (and caught)
# msg : Any additional messaging
# func : A simple function to pass the message to (optional)
# If "func" is supplied, ErrMsg uses it for output instead of printing to stdout
def ErrMsg(err,msg,func=None,prefix=None,callerframe=None):
	"""
	Wrapper function to print an Exception error message.
	It also includes the line number and file where the error occurred
	Technically, only active when in CmdLineMode.
	"""

	# Start by getting the callers frame
	if callerframe == None:
		callerframe = inspect.currentframe().f_back

	module = callerframe.f_code.co_filename
	line = callerframe.f_lineno

	expmsg = repr(err)

	prefix = prefix if prefix else ">>> "

	compiled = "{} Exception mod({}) line({}) {}\n{}".format(prefix,module,line,msg,expmsg)

	Msg(compiled,func)

# Running Time Helper
def RunningTime():
	"""Running Time Helper (Yes, I know these already exist)"""

	startTime = datetime.now()

	def Stop():
		"""Calculate Runtime From Given Start Time"""

		nonlocal startTime

		td = datetime.now() - startTime

		return td

	return Stop

# Running Time Decorator
def TimeMe(func):
	"""Time a function call"""

	@functools.wraps(func)
	def wrapper(*args,**kwargs):
		startTime = datetime.now()

		results = func(*args,**kwargs)

		endTime = datetime.now()

		return (endTime - startTime), results

	return wrapper

#
# Generic Helper Functions
#

# Parse Delimited Strings
def ParseDelimitedString(input_str,delimiters="'\"",separator=" "):
	"""Parse An Input String that May have delimited text into an array"""

	L = list()
	S = Stack()

	buffer = ""

	in_delimited_space = False
	string_length = len(input_str)

	for index in range(0,string_length):
		c = input_str[index]
		stack_length = S.len()

		if not in_delimited_space and c == separator:
			DbgMsg(f"{buffer} '{c}' {index}")
			L.append(buffer)
			buffer = ""
		elif c in delimiters and (c == S.peek() or stack_length == 0):
			if stack_length == 0:
				in_delimited_space =  True
				S.push(c)
			else:
				in_delimited_space = False
				S.pop()

			continue
		else:
			buffer += c
	else:
		if S.len() == 0:
			L.append(buffer)
		else:
			tmp = S.peek() + buffer
			L.extend(tmp.split(separator))

	return L

# Max Size of String In List
def MaxSize(lst):
	"""
	Given a list (of strings or iterable items), return the item of the largest size.
	"""
	max = 0

	for item in lst:
		x = len(item)
		max = x if x > max else max

	return max

# Progress Bare
def ProgressBar(trail=".",prog_func=None):
	"""Print a breadcrumb for a trail each time this is called"""

	def Next():
		if prog_func:
			prog_func()
		else:
			print(trail,end='',flush=True)

	return Next

# Pause With Prompt
def Pause(prompt=None,pause=0,no_msg=False, default=None):
	"""
	Pause with a prompt for for a given number of seconds
	Only active in CmdLineMode.
	"""
	reply = default

	if ModuleMode(): return reply

	if prompt is None:
		prompt = "Hit ENTER to continue"

	if pause > 0 or type(prompt) is int:
		if type(prompt) is int:
			pause = prompt
			prompt = None

		if not no_msg:
			msg = f"Pausing for {pause} seconds" if prompt is None else prompt
			Msg(msg)

		# Maybe add key to break out of sleep??? And then return input?

		time.sleep(pause)
	else:
		reply = input(prompt)

	return reply

# Prompt with Reply Convenience Function
def Ask(prompt,pause=0, default=None):
	"""Convenience Function for Pause to act as prompt with reply"""

	return Pause(prompt,pause,no_msg=False,default=default)

# Alias for Ask
Prompt = Ask

def AnyKey(msg, pause=0, default=None, keyonly=False):
	"""Pause For A Key Hit With Timeout"""

	result = default

	if msg is not None:
		Msg(msg)

	startTime = datetime.now()
	expired = False

	if os.name == 'nt':
		import msvcrt

		while not msvcrt.kbhit():
			time.sleep(0.25)

			td = datetime.now() - startTime

			if pause > 0 and td.seconds >= pause:
				expired = True
				break

		if keyonly and not expired:
			result = msvcrt.getwch()
		elif not keyonly and not expired:
			result = input()
	else:
		import termios

		# Set to be non-blocking

		fd = sys.stdin.fileno()

		oldterm = termios.tcgetattr(fd)
		newattr = termios.tcgetattr(fd)
		newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
		termios.tcsetattr(fd, termios.TCSANOW, newattr)

		try:
			result = sys.stdin.read(1)
		except IOError:
			pass
		finally:
			termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

	return result

#
# File, Folder and Temp File Helpers
#

# Create a temp filename (with optional postfix)
def TmpFilename(postfix=None,nopath=False,prefix=None,file=None,folder=None):
	"""
	Low Rent Wrapper to Generator Random Temporary Temp Filenames.
	The purpose is to simulate the old Unix tmpname function. This
	is not super safe to use, security-wise. The caller can supply
	a postfix for the file. (i.e. like .bak, etc)
	The function will attempt to ascertain what the system temp folder
	is before generating the path and check for a conflict. If nopath
	is true, only a random file name is returned.
	"""

	length = random.choice(range(4,10))

	rname = lambda k: "".join(random.choices("abcdefghijklmnopqrstuvwxyz1234567890",k=k))

	if not postfix:
		postfix = ""

	if not prefix:
		prefix = ""

	# User can screw themselves up here by providing file and folder, file wins in this case
	if folder != None: folder = os.path.abspath(folder)
	if file != None: folder = os.path.abspath(os.path.dirname(file))

	if sys.platform == "win32" and folder == None:
		folder = os.environment.get("TMP") or os.environment.get("TEMP")

		if not folder:
			folder = r"C:\Windows\System32\temp"
	elif (sys.platform == "linux" or sys.platform == "macos") and folder == None:
		folder = "/tmp"

	if nopath:
		tmp = rname(length)
	else:
		file_exists = True

		while file_exists:
			fname = rname(length)

			tmp = os.path.join(folder,"{}{}{}".format(prefix,fname,postfix))

			file_exists = os.path.exists(tmp)

	return tmp

# Make sure a given name does not clobber an existing file and return a new name if it does
def NoClobber(fname,postfix=" ({})"):
	"""
	Make sure a filename does not clobber and existing file.
	If does collide with an existing file, find a name that does not
	based on saving the file with a number appended to the end of it.
	"""

	if os.path.exists(fname):
		folder, file = os.path.split(fname)
		f_noext, ext = os.path.splitext(file)

		count = 1

		fmtstr = "{}" + postfix + "{}"

		fm = lambda p,b,c,x: os.path.join(p,fmtstr.format(b,c,x))

		fname = fm(folder,f_noext,count,ext)

		while os.path.exists(fname):
			count += 1
			fname = fm(folder,f_noext,count,ext)

	return fname

def SafeIO(*files):
	"""A Low Budget (and Low Reliability) File Locking Decorator"""

	"""
	How it works:
	Each supplied filename gets a lock in the form of an empty file with the same filename plus an extension of ".protected"
	Any function decorated with this and having the same file or file list, will be prevented from accessing the file or files
	until the locks are removed. When the decorated function terminates (or throws an unhandled exception), the locks are
	automatically removed.

	Things to note, any function NOT decorated with this, WILL be able to access any of the "protected" files.
	Any program or script outside of the one using this WILL also have access to the files. This is not a low level file
	system lock. *IF* a python script outside the one is using this decorator and also uses this decorator with a similar
	file or list of files, will also be locked out.

	If this decorator crashes or the greater calling script crashes, the locks may remain in place. You will have to programmatically
	remove the locks yourself.

	Deadlocks or starvation CAN occur if protecting multiple files, only one file is polled for protection (or lock created) at any one time.
	"""

	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):

			dbgblk, dbglb = DbgNames(SafeIO)

			DbgEnter(dbgblk, dbglb)

			ext = ".protected"

			# Protect files from write
			for file in files:
				pro = f"{file}{ext}"

				if DebugMode() and os.path.exists(pro):
					DbgMsg(f"{file} is protected", dbglabel=dbglb)

				while os.path.exists(pro):
					time.sleep(0.1)

				Touch(pro)

			# Files are protected

			results = None
			fblk, flb = DbgNames(func)

			try:
				results = func(*args, **kwargs)
			except Exception as err:
				ErrMsg(err, f"An error occurred while executing a SafeIO decorated function {fblk}, cleaning up locks")

			# clean up
			for file in args:
				pro = f"{file}{ext}"

				if os.path.exists(pro):
					os.remove(pro)
					DbgMsg(f"Removed lock for {file}", dbglabel=dbglb)

			DbgExit(dbgblk, dbglb)

			return results
		return wrapper
	return decorator

#
# Printing Strings/Headers/Aligners Helpers
#

# None or Empty Evaluation for strings
def EmptyOrNone(buffer):
        """Determine if String is Empty and None"""

        return (buffer == None or buffer == "")

# Convert Value To Kilobytes
def Kilobytes(value,units=1024):
	"""Convert Value To Kilobytes"""

	return round(value / units,2)

# Convert Value To Megabytes
def Megabytes(value,units=1024):
	"""Convert Value To Megabytes"""

	return round(Kilobytes(value,units=units) / units,2)

# Convert Value To Gigabytes
def Gigabytes(value,units=1024):
	"""Convert Value To Gigabytes"""

	return round(Megabytes(value,units=units) / units,2)

# Convert Value To Terabytes
def Terabytes(value,units=1024):
	"""Convert Value To Terabytes"""

	return round(Gigabytes(value,units=units) / units,2)

# Convert Value To Petabytes
def Petabytes(value,units=1024):
	"""Convert Value To Petabytes"""

	return round(Terabytes(value,units=units) / units,2)

# Convert Value To Exabytes
def Exabytes(value,units=1024):
	"""Convert Value To Exabytes"""

	return round(Petabytes(value,units=units) / units,2)

# Best Units tring
def BestUnits(value,units=1,space=1):
	"""
	Convert Value In Readable Units String

	This function will determine the best unit fit for a value
	(KB,MB,GB and so forth) and return it as a string for printing

	Units is the size of the abbreviation, 1 = 1 letter, 2 = 2 letters, 3 = fulle word

	"""

	abbr = {}
	abbr[0] = [ "B", "B", "Bytes" ]
	abbr[1] = abbr[0]
	abbr[2] = abbr[0]
	abbr[3] = [ "K", "KB", "Kilobytes" ]
	abbr[4] = abbr[3]
	abbr[5] = abbr[3]
	abbr[6] = [ "M", "MB", "Megabytes" ]
	abbr[7] = abbr[6]
	abbr[8] = abbr[6]
	abbr[9] = [ "G", "GB", "Gigabytes" ]
	abbr[10] = abbr[9]
	abbr[11] = abbr[9]
	abbr[12] = [ "T", "TB", "Terabytes" ]
	abbr[13] = abbr[12]
	abbr[14] = abbr[12]
	abbr[15] = [ "P", "PB", "Petabytes" ]
	abbr[16] = abbr[15]
	abbr[17] = abbr[15]
	abbr[18] = [ "E", "EX", "Exabytes" ]
	abbr[19] = abbr[18]
	abbr[20] = abbr[18]

	oom = 0 if value == 0 else int(math.floor(math.log10(value)))
	msg = ""

	ws = " " * space

	units -= 1

	if units > 2: units = 2
	if units < 0: units = 0

	if oom < 3:
		pass
	elif oom < 6:
		value = Kilobytes(value)
	elif oom < 9:
		value = Megabytes(value)
	elif oom < 12:
		value = Gigabytes(value)
	elif oom < 15:
		value = Terabytes(value)
	elif oom < 18:
		value = Petabytes(value)
	else:
		value = Exabytes(value)

	msg = f"{value}{ws}{abbr[oom][units]}"

	return msg

# Count line in text content
def LineCount(filename=None,buffer=None,file=None):
	"""
	Count lines in supplied object

	The object can be a string buffer, filename to be read or
	and open file handle. Open file handles will not be closed
	"""

	line_count = 0

	if buffer != None:
		file = io.StringIO(buffer)
	elif filename != None:
		file = open(filename,"r")

	if file != None:
		for line in file:
			line_count += 1

		if filename != None: file.close()
	else:
		raise ValueError()

	return line_count

# Count words in text content
def WordCount(filename=None,buffer=None,file=None):
	"""
	Count words and Lines in supplied object

	The object can be a string buffer, filename to be read or
	and open file handle. Open file handles will not be closed

	Returns the tuple (word_count,line_count)
	"""

	word_count = 0
	line_count = 0

	splitter = re.compile(r"\s+")

	if buffer != None:
		file = io.StringIO(buffer)
	elif filename != None:
		file = open(filename,"r")

	if file != None:
		for line in file:
			line_count += 1
			word_count += len(splitter.split(line))

		if filename != None: file.close()
	else:
		raise ValueError()

	return word_count, line_count

# Clear Screen
def Clear(altmethod=False):
	"""
	Clear screen the ANSI Way.
	If altmethod is true, use the less safe way
	Only active when in CmdLineMode.
	"""
	result = 0

	if CmdLineMode():
		if altmethod:
			result = subprocess.call(["clear"])
		else:
			# Clear Screen, the ANSI way
			print(chr(27)+'[2j')
			print('\033c')
			print('\x1bc')

	return result

# Print Newline
def NewLine(output=True):
	"""Wrapper to print a newline, only active in CmdLineMode"""

	nl = "\n"

	if output: Msg("")

	return nl

# Create a Bar for printing the size og the given string
def Bar(msg,line="=",output=True):
	"""
	Function to create a bar line that same length as the given string.
	The default line is "=", but you can supply others through the "line" parameter
	"""
	l = len(msg)

	return (line * l)

# Combine Message and Bar in one string with a new line seperator
def CombiBar(msg,line="=",prefix="",postfix=""):
	"""
	Combine a message and bar into one string with a new line seperator.
	Basically, it creates a header.
	"""
	line = Bar(msg,line)

	return prefix + msg + postfix + "\n" + prefix + postfix + line

# Align a string in a manner that everything lines up nicely according to the size of the largest item
def Align(items,descriptions=None,sep=" ",sepcount=1,prefix="",postfix="",midfix=""):
	"""
	Given a list of items in a dictionary, make sure the value column lines up together when the
	key and value are placed into a single string for presentation. If the items list is not a
	dictionary, and descriptions are supplied, the items and descriptions are zipped together and
	turned into a dictionary. If only a list is supplied (and no descriptions), the function returns
	an empty list.
	"""

	packed = list()

	if type(items) == list and descriptions == None:
		return packed

	if type(items) == list:
		biggest = MaxSize(items)
	else:
		biggest = MaxSize(items.keys())

	# If descriptions not empty, assume there is a matching list
	if descriptions:
		zipped = zip(items,descriptions)

		items = dict(zipped)

	# Items is always assumed to be a dictionary
	for item,description in items.items():
		l = len(item)

		packed.append(prefix + str(item) + (sep * (biggest - l + sepcount)) + (midfix + sep if midfix != None and not midfix == "" else "") + str(description) + postfix)

	return packed

# Wrapper for Align (Backwards Compatibility Wrapper)
def Pack(items,descriptions=None,sep=" ",sepcount=1,prefix="",postfidx=""):
	"""Backward compatibility wrapper for the newer Align function"""

	return Align(items,descriptions,sep,sepcount,prefix,postfix)

# Print Packed Lines
def PrintAligned(items,descriptions=None,sep=" ",sepcount=1,prefix="",postfix="",midfix=""):
	"""
	Uses the Align function to combine elements in a string in an aligned manner and prints it.
	Only active when in CmdLineMode.
	"""
	for line in Align(items,descriptions,sep,sepcount,prefix,postfix,midfix=midfix):
		Msg(line)

# Wrapper for PrintAligned (Backwards Compatibility Wrapper)
def PrintPacked(items,descriptions=None,sep=" ",sepcount=1,prefix="",postfix="",midfix=""):
	"""Backward compatibility wrapper for the newer PritnAligned function"""
	PrintAligned(items,descriptions,sep,sepcount,prefix,postfix)

# Menu of Items
def Menu(selectables,prompt="Enter Selection and press ENTER",extra_options={}, no_match=False):
	"""
	Given a list of items, present a numbered menu for a user to select AN item from
	until a valid item is selected or the menu quit.
	"""

	selected = None

	if ModuleMode(): return selected

	while True:
		count = 1

		options = {}

		for choice in selectables:
			options[str(count)] = choice
			count += 1

		for option,choice in extra_options.items():
			options[option] = choice

		for option,choice in options.items():
			print("{}. {}".format(option,choice))


		NewLine()

		reply = input(f"{prompt} ")

		if reply in options.keys():
			selected = options[reply]
			break
		elif no_match: # If no match is ok, return it.
			selected = reply
			break
		elif reply == "quit": # Hidden Escape Hatch
			break
		else:	# Repeat Menu
			print("Not a valid option")
			Pause(pause=3,no_msg=True)
			Clear()

	return selected

#
# Choosey Selectors
#

# Determine if any pattern in list exists in data
def substrof(pattern_list,data):
	"""Determine if any substring pattern in list is in data"""

	flag = False

	for item in pattern_list:
		if item in data:
			flag = True
			break

	return flag

# Return Fallback if item is equal to any value in list
def isany(item,fallback,possibles=[]):
	"""if item is any of the objects/values in the list of possibles, return the fallback, otherise, return the item"""

	for possible in possibles:
		if item == possible:
			return fallback

	return (item)

# Determine if any item in grp1 is in grp2
def hasany(grp1,grp2):
	"""
	See if the grp2 list has any item from grp1 in it
	"""

	result = False

	for item in grp1:
		if item in grp2:
			result = True
			break

	return result

def inlist(item,item_list):
	"""Determine if item is in List"""

	return (item in item_list)

# Select an Item From A Result Set
def Choose(results,prefix=None,seperator="/",header="Select One\n==========",prompt="\nSelect number of item : "):
	"""
	Select an item from a result set
	"""

	index = 0
	result = None

	if CmdLineMode():
		Msg(header)
		for item in results:
			if type(item) is list:
				item = ",".join(item)
			elif not type(item) is str:
				item = str(item)

			if prefix:
				print("{}. {}{}{}".format(index,prefix,seperator,item))
			else:
				print("{}. {}".format(index,item))

			index +=1

		index = input(prompt)

		if index != "":
			try:
				index=int(index)

				result = results[index]
			except:
				result = None

		return result

#
# Oddball Helpers (Many time based)
#

# Convert Data to Date @ Midnight
def Midnight(date_in=None):
        """Alias for Start of Day"""

        return StartOfDay(date_in)

# Alias for Midnight
def StartOfDay(date_in=None):
        """Convert Date to Start of Day"""

        d = None

        if date_in == None:
                d = datetime.now().date()
        elif type(date_in) is datetime:
                d = date_in.date()
        elif type(date_in) is date:
                d = date_in

        t = dt.time(0,0,0)

        nd = datetime.combine(d,t)

        return nd

# Convert DateTime to End of Day (Just before midnight)
def EndOfDay(date_in=None):
        """Convert Date to End of Day"""

        d = None

        if date_in == None:
                d = datetime.now().date()
        elif type(date_in) is datetime:
                d = date_in.date()
        elif type(date_in) is date:
                d = date_in

        t = dt.time(23,59,59)

        nd = datetime.combine(d,t)

        return nd


# Do Something N Times Only
def DoTimes(func,times=1):
	"""
	Execute something only the specified number of times indicated.
	"""
	count = 0

	# Used to Fire the embedded function
	def Fire(funcparam=None):
		"""
		Execute a function with optional parameter
		"""
		nonlocal count

		result = None

		if count < times:
			if funcparam:
				result = func(funcparam)
			else:
				result = func()

			count += 1

		return result

	return Fire

# Do something when a condition is met
def DoCondition(func,condition):
	"""
	Execute something, ONLY with the condition function says so.
	The condition function returns a True or False value
	"""

	def Check(funcparam=None,conparam=None):
		"""
		Check to see if condition is met, then execute function if so.
		You can supply an optional parameter to the fnction and an
		optional parameter to the conditional
		"""
		condition_met = False

		if conparam:
			condition_met = condition(conparam)
		else:
			condition_met = condition()

		result = None

		if condition_met:
			if funcparam:
				result = func(funcparam)
			else:
				result = func()

		return result

	return Check

# Do Something at a given Date/Time
def DoWhen(func,timestamp):
	"""
	Execute a function at a given Date/Time.
	This is not like cron, it expects that this will be evaluated
	periodically (for example in a loop) and will occur shortly after
	the given Date/Time passes
	"""

	def Check(funcparam=None):
		"""
		Check to see if the give Date/Time has passed and if so, execute
		the function.
		"""

		result = None

		if timestamp < datetime.now():
			if funcparam:
				result = func(funcparam)
			else:
				result = func()

		return result

	return Check

# Rate Limit Execution Helper
def RateLimit(func,times_per_interval,interval,sleep=None,gap=None):
	"""
	A helper designed to rate limit a function to execute a given number of times per second.
	The number of times in total, must be controlled outside this helper. The helper will
	pause the function (and the whole script) until it can run again. It pauses in 0.25s
	intervals until the next run. interval must be a time delta.
	If gap is provided, there will be a forced gap of time between runs.
	Sleep and gap intervals use Python's time.sleep() function.
	"""
	interval_start = None
	next_interval = None
	run_count=0

	# Run Rate Limited Function
	def RateLimitMe(funcparam=None):
		"""
		Run function if within rate limits, otherwise pause execution until the end of the defined internval
		"""

		nonlocal interval_start, run_count, next_interval

		if interval_start == None: interval_start = datetime.now()

		next_interval = interval_start + interval

		if run_count >= times_per_interval and datetime.now() < next_interval:
			run_count = 0

			while datetime.now() < next_interval:
				if sleep == None:
					time.sleep(0.25)
				else:
					time.sleep(sleep)


			interval_start = datetime.now()

		if funcparam != None:
			result = func(funcparam)
		else:
			result = func()

		if gap != None:
			time.sleep(gap)

		run_count += 1

		return result

	return RateLimitMe

#
# File Helpers
#

# Save To File
def SaveToFile(fname,data,option="wt",delimiter=","):
	"""
	Low Rent Wrapper for Saving data to a file
	"""
	with open(fname,option) as output:
		if option == "wt" or option == "at":
			output.write(str(data),delimiter=delimiter)
		elif option == "wb" or option == "ab":
			if type(data) == str:
				data = data.encode("utf-8")

			output.write(data)

# Remove Rows From On Disk csv (Badly named)
def RemoveRowsFromFile(fname,index=None,column=None,pattern=None,count=-1,fieldnames=None,delimiter=","):
	"""
	Remove Row(s) from On Disk CSV (or CSVDict)

	If index is given, the row number with the given index is removed
	If column is given, then the column is searched for "pattern", an RE Expression
	When count is provided only "count" rows are deleted
	"""

	removed = 0

	tmpfname = TmpFilename()

	with open(fname,"r",newline="") as f_in:
		reader = None

		if fieldnames:
			reader = csv.DictReader(f_in,fieldnames,delimiter=delimiter)
		else:
			reader = csv.reader(f_in,delimiter=delimiter)

		with open(tmpfname,"w",newline="") as f_out:
			writer = None

			if fieldnames:
				writer = csv.DictWriter(hf,fieldnames,delimiter=delimiter)
			else:
				writer = csv.writer(hf,delimiter=delimiter)

			position = 0
			for row in reader:
				if index:
					if index != position and (count == -1 or removed < count):
						writer.write(row)
					else:
						removed += 1
				else:
					if not re.search(pattern,row[column]) and (count == -1 or removed < count):
						writer.write(row)
					else:
						removed += 1

				position += 1

	if removed > 0:
		SwapFile(tmpfname,fname)

	return removed

# CSV Reader Helper (work into iterator thingy)
def LoadCSV(fname,delimiter=",",warn=False):
	"""
	Low Rent Wrapper for opening a basic CSV File and extracting the rows
	"""
	rows = list()

	if warn and not os.path.exists(fname):
		Msg("File {} does not exist".format(fname))
		return rows

	with open(fname,newline='') as csvfile:
		reader = csv.reader(csvfile,delimiter=delimiter)

		for row in reader:
			rows.append(row)

	return rows

# Save CSV Data to File
def SaveCSV(fname,rows,mode="w",delimiter=","):
	"""
	Low Rent Wrapper for saving tabular/columnar data to a CSV file.
	"""
	with open(fname,mode,newline='') as csvfile:
		writer = csv.writer(csvfile,delimiter=delimiter)

		for row in rows:
			writer.writerow(row)

# Append Items to CSV File
def AppendCSV(fname,items,delimiter=","):
	"""
	Low Rent Wrapper to Append A Row (tabular/columnar) data to a basic
	CSV file.
	"""

	SaveCSV(fname,items,mode="a",delimiter=delimiter)

# Remove Rows From CSV on Disk
def RemoveFromCSV(fname,index=None,column=None,pattern=None,count=-1,delimiter=","):
	"""Remove Row(s) from On Disk CSVDict"""

	return RemoveRowsFromFile(fname,index,column,pattern,count,None,delimiter)

# Load CSV as Dictionary
def LoadCSVDict(fname,fieldnames=None,delimiter=","):
	"""
	Low Rent Wrapper for opening CSV files with (or without a header) and the
	caller wants it in dictionary format.

	If fieldnames is supplied, the first line is considered row data
	If fieldnames are not supplied, the first line is assumed to be a header line
	"""
	rows = list()

	with open(fname,newline='') as csvfile:
		reader = csv.DictReader(csvfile,fieldnames=fieldnames,delimiter=delimiter)

		for row in reader:
			rows.append(row)

	return rows

# Save tabular data to CSV with column headers included
def SaveCSVDict(fname,rows,fieldnames,mode="w",delimiter=","):
	"""
	Low Rent Wrappper for saving CSV with a header.

	The rows can be a dictionary or just a list. When a list, the items
	are written in order.
	"""

	with open(fname,mode,newline='') as csvfile:
		writer = csv.DictWriter(csvfile,fieldnames=fieldnames,delimiter=delimiter)

		if not mode in [ "a", "at" ]:
			writer.writeheader()

		for row in rows:
			writer.writerow(row)

# Append Tablular data to CSV with column headers
def AppendCSVDict(fname,rows,fieldnames,delimiter=","):
	"""
	Low Rent Wrapper for append to CSVDict
	"""

	SaveCSVDict(fname,rows,fieldnames,mode="a",delimiter=delimiter)

# Remove Rows From CSVDict on Disk
def RemoveFromCSVDict(fname,index=None,column=None,pattern=None,count=-1,fieldnames=None,delimiter=","):
	"""Remove Row(s) from On Disk CSVDict"""

	return RemoveRowsFromFile(fname,index,column,pattern,count,fieldnames,delimiter)

# Extract Data From File
def ExtractFromFile(expression,src,dst=None,columns=None,mode="w"):
	"""
	Extract Data From Text Based Line Oriented File

	The expression should be a regular expression with named
	capture groups, i.e. (?P<name>.+)

	If an output/destination filename is provided, the data willbe dumped as a CSV

	The default mode is "w" on the output file, use "a" to append to an exiting file
	"""

	selected_data = list()

	exp = re.compile(expression)

	with open(src,"r") as f_in:
		writer = None
		file = None

		if dst != None:
			file = open(dst,mode,newline='')
			if columns != None:
				writer = csv.DictWriter(file,columns)
				writer.writerheader()
			else:
				writer = csv.writer(file)

		for line in f_in:
			match = exp.search(line)

			if match != None:
				# named groups to list

				groups = match.groupdict()

				items = groups.values()

				if writer != None:
					writer.writerow(items)
				else:
					selected_data.append(items)

		if file != None: file.close()

	return items

# Check to see if value is in a column of tabular data
# Return first match
def IsInColumn(item,rows,column=0):
	"""
	Wrapper function to look for an item in tabular/columnar data.
	The function returns the row with the first match.
	"""
	result = None

	for row in rows:
		if item == row[column]:
			result = row
			break

	return result

# Check Tabular/Columnar Data With a Regular Expresion
def IsInColumnRe(expresion,rows,column=0):
	"""
	Wrapper function to look for a pattern in a column of tabular/columnar data with
	a regular expression. If a cell is not a string, it will be converted
	into one first.
	"""

	result = None

	expr = re.compile(expression)

	for row in rows:
		if expr.search(str(row[column])):
			result = row
			break

	return result

# Search a column of tabular data, return all matching results
def SearchColumn(item,rows,column=0,return_all=True):
	"""
	Wrapper function to look for an item in tabular/columnar data.
	The function looks for all occurrences and returns the rows in
	a list.
	"""
	results = list()

	for row in rows:
		if item == row[column]:
			if return_all:
				results.append(row)
			else:
				return row

	return results

# Search Tabular/Columnar Data With a Regular Expresion
def SearchColumnRe(expresion,rows,column=0,return_all=True):
	"""
	Wrapper function to search a column of tabular/columnar data with
	a regular expression. If a cell is not a string, it will be converted
	into one first.
	"""

	results = list()

	expr = re.compile(expression)

	for row in rows:
		if expr.search(str(row[column])):
			if return_all:
				results.append(row)
			else:
				return row

	return results

# Check Entire CSV for an Item
def IsIn(item,rows):
	"""
	Seach Entire CSV (all columns of all rows) for an item
	"""

	within = False

	for row in rows:
		if item in row:
			within = True
			break

	return within

# Print JSON Doc Neatly
def PrintJSON(jdoc,indent=2):
	"""Convenience Function To Print JSON Doc Neatly"""
	msg=None

	if jdoc:
		msg = json.dumps(jdoc,indent=indent)

	print(msg)

# Wrapper Function for Loading JSON
def LoadJSON(fname):
	"""
	Wrapper function to load a JSON File
	"""
	data = None

	with open(fname,"r") as json_file:
		data = json.load(json_file)

	return data

# Create An Audit Log Entry
def AuditEntry(eventname,comment):
	"""Convenience function for creating an Audit Log Entry"""

	entry = [ eventname, comment ]

	return entry

# Audit Trail Log Helpers (CSV)
# Format: Datestamp,EventName,Comment
def AuditTrail(fname,row,delimiter=","):
	"""
	Wrapper function to append a row of data to a file that is essentially
	and audit trail log.
	"""

	if type(row) == list:
		DbgMsg("Inserting time into row... list",dbglabel="py_helper")
		row.insert(0,datetime.now())
	elif type(row) == dict:
		DbgMsg("row is dict",dbglabel="py_helper")
		row = row.values()
		row.insert(0,datetime.now())
	elif type(row) == str:
		DbgMsg("row is str",dbglabel="py_helper")
		row = [ datetime.now(), row ]
	else:
		raise ValueError("Parameter in audit trail is neither list, dict or string")

	DbgMsg("Calling AppendCSV",dbglabel="py_helper")

	AppendCSV(fname,[ row ],delimiter=delimiter)

	DbgMsg("Exiting AuditTrail",dbglabel="py_helper")

# Dump the contents of a File
def Dump(fname):
	"""
	Wrapper function to dump the contents of a file to the screen after clearing the screen first.
	Only functions when module is in CmdLineMode.
	"""

	if ModuleMode(): return False

	Clear()

	with open(fname,"r") as dumpfile:
		for line in dumpfile:
			Msg(line.strip())

		NewLine()

	return True

# Create File if it doesn't exit and/or append header to it
def Touch(fname,header=None,src_file=None,perms=None):
	"""
	Low Rent Wrapper to simulate the "touch" command, with optional
	header data. Will also create folders if needed.
	"""

	base_name = os.path.basename(fname)
	dir_name = os.path.dirname(fname)

	if not os.path.exists(dir_name):
		os.makedirs(dir_name,exist_ok=True)

	if not os.path.exists(fname):
		with open(fname,"a") as the_file:
			if header:
				the_file.write(header)

	if src_file != None:
		shutil.copystat(src_file,fname)

	if perms != None:
		os.chmod(fname,perms)

# Cmdline Tool as Python Function
def Cut(delimiter=",",fields=[],f_in=sys.stdin,f_out=sys.stdout,buffer=None,output_delimiter=None):
	"""Unix CmdLine Tool As a Python Function"""

	# Get Fields From Line
	def GetFields(items):
		"""Get Fields from Line"""

		selected_fields = list()
		output = None

		for field in fields:
			if type(field) == int:
				item = items[field]
				selected_fields.append(item)

			elif type(field) == range:
				for index in field:
					selected_fields.append(items[index])

		output = output_delimiter.join(selected_fields)

		return output

	# Process File Iteratively
	def ProcessIter():
		"""Process File Iteratively"""

		for line in f_in:
			items = line.split(delimiter)

			output = GetFields(items)

			yield output

	output = None

	output_delimiter = delimiter if output_delimiter == None else output_delimiter

	if buffer != None:
		items = buffer.split(delimiter)

		output = GetFields(items)
	elif f_out != None:
		for item in ProcessIter():
			f_out.write(item+"\n")
	else:
		output = ProcessIter()

	return output

# Copy a file
def CopyFile(src_fname,dst_fname,follow_symlinks=True):
	"""
	A simple shell function for calling copyfile
	"""
	shutil.copyfile(src_fname,dst_fname,follow_symlinks=follow_symlinks)

# Swap File
def SwapFile(new_file,old_file,keep_old=False):
	"""
	A wrapper function to swap the names of files.
	By default, the old file is deleted. If keep_old is set
	to True, then the old file will be named renamed to the
	new file and the new file renamed to the old file.
	This utilizes the shutil.move function on the new file.
	"""

	if os.path.exists(old_file) and not keep_old:
		os.remove(old_file)
		shutil.move(new_file,old_file)
	elif os.path.exists(old_file) and keep_old:
		# We start by renaming the "old_file" to something temporary
		tmp = "{}_{}tmp".format(old_file,random.randint(1000,10000))

		os.rename(old_file,tmp)

		shutil.move(new_file,old_file)

		shutil.move(tmp,new_file)


# Simple File Backup
def BackUp(fname,backup=None):
	"""
	Low Rent Backup Wrapper. Simply Copies the supplied file
	to the backup name.
	If the back currenly exists, it is deleted. If the given file
	does not exist, it is Touched, then copied (which is a waste
	of time, but at least it doesn't error out)
	"""
	bkup_fname = None

	if backup:
		bkup_fname = backup
	else:
		bkup_fname = fname + ".bak"

	if os.path.exists(bkup_fname):
		os.remove(bkup_fname)

	if not os.path.exists(fname):
		Touch(fname)

	shutil.copyfile(fname,bkup_fname)

# Restore Simple Backup (if it exists)
def Restore(fname,backup=None):
	"""
	Restore a file backed up with BackUp over the existing file.
	If the current file still exists, it is deleted and the backup
	is copied into place, leaving the backup file as is.
	"""
	bkup_fname = None

	if backup:
		bkup_fname = backup
	else:
		bkup_fname = fname + ".bak"

	if os.path.exists(bkup_fname):
		if os.path.exists(fname): os.remove(fname)

		shutil.copyfile(bkup_fname,fname)

# Edit a file with an external Command/Editor (Defaults: Unix = Nane, Windows = notepad)
def Edit(source,create=False,app=None):
	"""
	Edit a file using an external app. If not defined, none is selected for Unix and notepad selected for windows.
	If create is true and the file does not exist, it's created first.
	If file does not exist and create is false, it is assumed that "source" is the content
	to be editted and is returned as the result.
	"""
	result = 0

	if CmdLineMode():
		cmd = "nano"

		if sys.platform == "win32":
			cmd = "notepad.exe"

		if app:
			cmd = app

		if os.path.exists(source):
			result = subprocess.call([cmd,source])
		elif create:
			Touch(source)
			result = subprocess.call([cmd,source])
		else:
			tmpfile = TempFilename()

			SaveToFile(tmpfile,source)

			result = subprocess.call([cmd,tmpfile])

			if result == 0:
				with open(tmpfile,"rt") as file:
					result = file.read()

				os.remove(tmpfile)

	return result

# Edit Buffer In External Editor
def EditBuffer(buffer,prompt=False):
	"""
	Edit a string buffer in an external editor

	If input buffer/string remains unchanged, None is returned
	"""

	tmp = TmpFilename()
	new_buffer = ""

	with open(tmp,"w") as f_out:
		f_out.write(buffer)

	Edit(tmp)

	with open(tmp,"r") as f_in:
		new_buffer = f_in.read()

	os.remove(tmp)

	response = "y"

	if prompt:
		response=input("Keep (y/n)? ")

	if buffer == new_buffer or response.lower() == "n":
		new_buffer = None

	return new_buffer

# Page File to screen using pydoc
def Page(source):
	""" Page a file to screen using pydoc, if source is a file, the file is read in, if not, source is assumed to be text to page """
	if os.path.exists(source):
		with open(source,"rt") as data:
			pydoc.pager(data.read())
	else:
		pydoc.pager(source)

# Get an MD5 Hash of given file
def GetMD5Hash(fname):
	"""Generate the MD5 hash of a given file"""
	hash = None

	with open(fname,"rb") as file:
		hash = hashlib.md5(file.read()).hexdigest()

	return hash

# Get SHA256 Hash of given file
def GetSHA256Hash(fname):
	"""Generate the SHA256 Hash of the given file"""
	hash = None

	with open(fname,"rb") as file:
		hash = hashlib.sha256(file.read()).hexdigest()

	return hash

# Get File CRC32
def GetCRC32(fname):
	"""Get a CRC32 Checksum of the given file"""
	crc = None

	with open(fname,"rb") as file:
		crc = zlib.crc32(file.read())

	return crc

def Gzip(filename,removeOriginal=True,removeArchive=True):
	"""GZip a File"""

	compressedFilename = f"{filename}.gz"

	try:
		if os.path.exists(compressedFilename) and removeArchive:
			os.remove(compressedFilename)

		with open(filename,"r") as uncompressedFile, gzip.open(compressedFilename,"wb") as compressedFile:
			shutil.copyfileobj(uncompressedFile,compressedFile,4096)

		if removeOriginal:
			os.remove(filename)
	except Exception as err:
		ErrMsg(err,f"An error occurred while trying to compress {filename} or removing an existing archive")

def Ungzip(filename,removeArchive=True,mode="w",clearOriginal=False):
	"""Un Gzip A File"""

	uncompressedFilename = filename.removesuffix(".gz")

	try:
		if os.path.exists(uncompressedFilename) and clearOriginal:
			os.remove(uncompressedFilename)

		with open(uncompressedFilename,mode) as uncompressedFile, gzip.open(filename,"rb") as compressedFile:
			shutil.copyfileobj(compressedFile,uncompressedFile,4096)

		if removeArchive:
			os.remove(compressedFilename)
	except Exception as err:
		ErrMsg(err,f"An error occurrred while trying to uncompress {filename} or removing the archive")

# Read List from file (will remove lines starting with a hash mark "#")
def ReadList(fname,mode="r",removecomments=True,splitter=None):
	"""
	Read a simple list from file that may contain line comments that start with a hash mark.
	Optionally retain the comments and optionally split the line using a custom splitter function.
	"""
	items = list()

	with open(fname,mode) as data:
		for line in data:
			match = re.search(r"^\s*#",line)

			if not match or not removecomments:
				# If not a comment, add to list

				line = line.strip()

				if splitter:
					items.append(splitter(line))
				else:
					items.append(line.strip("\n"))

	return items

# Write Simple List to file
def WriteList(fname,list,mode="w"):
	"""
	Write a simple list to file each list item is a new line
	"""
	with open(fname,mode) as data:
		for item in list:
			data.write(item + "\n")

# Append To A Simple List File
def AppendList(fname,list):
	"""
	Append to a simple list
	"""

	WriteList(fname,list,mode="a")

# Attempt to find a file as provided, with a single prefix, or a series of prefixes
def FindFile(prefix,filename,default=None):
	"""
	Given a list of parent folders (or a single folder), attempt to locate the file in those
	locations and return the fully qualified path. If a default is given, return the default
	if the file is not located.
	"""
	if not os.path.exists(filename):
		fname = os.path.basename(filename)

		if type(prefix) is str:
			filename=os.path.join(prefix,fname)

			if not os.path.exists(filename):
				filename = default
		else: # Assumes List
			for pre in prefix:
				filename = os.path.join(pre,fname)

				if os.path.exists(filename):
					break

				# If we are here and on the last prefix
				# select the default
				if pre == prefix[-1]:
					filename = default

	return filename

# LoadConfig Convenience Function
def LoadConfig(config_filename):
	"""Convenience function for loading a config.ini file"""

	appConfig = configparser.ConfigParser()

	appConfig.read(config_filename)

	return appConfig

#
# IP Stuff
#

# Check if supplied parameter is a valid formatted IP
def ValidIP(ip):
	"""
	Check supplied string of an IP Address to see if its a valid representation of an IP.
	Validated both IPv4 and IPv6
	"""

	flag=True

	try:
		ipo = ipaddress.ip_address(ip)
	except:
		flag = False

	return flag

# Check String to see if it's a valid IPv4 Addres
def IsIPv4(ip):
	"""
	Check to see if the supplied IP string is a valid IPv4 address
	"""

	flag = True

	try:
		ipo = ipaddress.IPv4Address(ip)
	except:
		flag = False

	return flag

# Check String to see if it's a valid IPv6 Address
def IsIPv6(ip):
	"""
	Check to see if the supplied IP string is a valid IPv4 Address
	"""

	flag = True

	try:
		ipo = ipaddress.IPv6Address(ip)
	except:
		flag = False

	return flag

# Check if String is valid IPv4 or IPv6 Network notation
def IsNetwork(network_str):
	"""
	Check to see if the supplied Network string is a Valid Network Notation
	"""

	return IsIPv4Network(network_str) or IsIPv6Network(network_str)

# Check if String is valid IPv4 CIDR Notation
def IsIPv4Network(network_str):
	"""
	Check to see if the supplied Network string is a Valid IPv4 CIDR
	"""

	flag = True

	try:
		neto = ipaddress.IPv4Network(network_str)
	except:
		flag = False

	return flag

# Check if String is valid IPv6 Network Notation
def IsIPv6Network(network_str):
	"""
	Check to see if the supplied Network string is a Valid IPv6 Network Notation
	"""

	flag = True

	try:
		neto = ipaddress.IPv6Network(network_str)
	except:
		flag = False

	return flag

#
# Convenience Conversion Functions
#

# Convert Dict to Lists
def DictToLists(dictionary,column=None):
	"""
	Convenience function to convert a dictionary into two seperate lista of
	keys and values. If column is defined and the returned values of the
	dictionary are lists, then only that column in the list is returned.
	"""

	keys = list(dictionary.keys())
	values = list(dictionary.values())

	if column and type(values) == list:
		values = [ v[column] for v in values ]


	return keys,values

# Convert Lists To Dictionary
def ListsToDict(keys,values,column=None):
	"""
	Convenience function to convert Lists Into a Dictionary.
	If column is defined and the values param is a list of lists, then
	only the column in each list is extracted for the value of
	the key.
	"""
	if column and type(values) == list:
		values = [ v[column] for v in values ]

	zipped = zip(keys,values)

	d = dict(zipped.__iter__())

	return d

# Convert a Key-Value CSV String To Dict
def KeyValueCSVStringToDict(kvpstr,separator=",",kvsep="="):
	"""Convert a string with key-value pairs separated via commas (or something else) into a dict"""

	d = dict()

	kvpairs = kvpstr.split(separator)

	for pair in kvpairs:
		key,value = pair.split(kvsep)

		d[key] = value

	return d

# Prompt if Config Section is Missing An Option
def PromptIfOptionMissing(section,option,prompt=None,cfgparser=None):
	"""Prompt if a config section is missing an option"""

	if cfgparser != None:
		section = cfgparser[section]

	reply = ""

	if not option in section.keys():
		prompt = prompt if prompt != None else "{} : ".format(option)

		reply = input(prompt)
	else:
		reply = section[option]

	return reply

#
# Using Python Modules as Plugins
#
# Note: plugin needs a "run()" function with a known argument list or a variable one (*argv or **kwarg) and both the caller and
# plugin has to know which one, the order of the parameters and/or the kwarg keys.
# Additionally, the module should include the requisite, "if __name__ == "__main__" statement for safety and sanity reasons.
# If you plan on NOT using the "run()" entry point, then the caller will have to know what functions to call during invocation.
#
# While this IS very similar to an import statement, it has three advantages over imports, first, the module can be anywhere
# in the file system, not just in the PYTHONPATH, second, you can load the modules at-will, lastly, this is a great way
# to customize and extend a single python script without altering the loading script very much.
#

# Load Python Module as Plugin
def LoadPlugin(plugin_module):
	"""Load a Plugin From Python Module File, provided as a path to that file"""

	DbgMsg(f"Loading Plugin module {plugin_module}")

	plugin = None

	try:
		if os.path.exists(plugin_module):
			importlib.invalidate_caches()

			module = os.path.basename(plugin_module)
			mpath = os.path.dirname(plugin_module)

			spec = importlib.util.spec_from_file_location(module,plugin_module)
			plugin = importlib.util.module_from_spec(spec)

			spec.loader.exec_module(plugin)
		else:
			Msg(f"{plugin_module} does not exist")
	except Exception as err:
		ErrMsg(err,f"An error occurred trying to load a plugin module {plugin_module}")

	DbgMsg(f"Loading Plugin module function complete")

	return plugin

# Load Plugins from Given Folder
def LoadPluginsFromFolder(folder,plugin_name=None,exclude=None):
	"""
	Load plugins from given folder

	If you provide the plugin name, it only attempts to load that one plugin.
	If a list, excluded, is provided, the items in the list are assumed to be base modules names
	(not absolute path names) and any module in the list is not loaded.

	The function returns a dictionary of (plugin_name,plugin_reference) pairs.

	The logic is that you can execute the plugin a so, plugins["plugin_name"].run(**kwargs)

	"""

	plugins = dict()

	if exclude == None: exclude = [ ]

	DbgMsg(f"Loading plugins from folder {folder}")

	for plugin in os.scandir(folder):
		if plugin.name in exclude: continue

		name,ext = os.path.splitext(plugin.name)

		if re.search(r".+\.py$",plugin.name):
			name,ext = os.path.splitext(plugin.name)

			if not plugin_name or plugin_name == name:
				DbgMsg(f"Registering {plugin.path}")
				pm = LoadPlugin(plugin.path)

				plugins[pm.Name] = pm

	DbgMsg(f"Loading plugins from folder {folder} completed")

	return plugins

#
# Plugin Registration
#
# Using these functions, you will register a plugin, but not load it.
# The intention here is to have a place holder, so that, when you
# want to use a plugin, it loads when it needs to be run.
# There is currently no way to unimport a module, officially, so
# we don't try here. However, the infrastructure for it exists if that
# ever changes.
#

# Plugin Entry Class
class PluginEntry:
	"""Entry for plugin management"""

	CreationTime = None
	"""Time this entry was created"""
	LoadTime = None
	"""Time Plugin was Loaded"""
	LastvUse = None
	"""Last Time Plugin was called, Caller Must Update this attribute"""
	Called = 0
	"""Call Count"""
	PluginModule = None
	"""Plugins Module (path and essentially, Name)"""
	ModuleReference = None
	"""Module Reference (pointer to loaded module/plugin)"""

	# Init Instance
	def __init__(self,plugin_module):
		"""Init Plugin Entry"""
		self.CreationTime = datetime.now()
		self.PluginModule = plugin_module

	# Print Contents of Plugin Entry
	def Print(self,silent=False):
		"""Print Plugin Entry Data"""

		fmtr = "{:<20} {}\n"

		msg = fmtr.format("Plugin Module", self.PluginModule)
		msg += fmtr.format("Creation Time", self.CreationTime)
		msg += fmtr.format("Load Time", self.LoadTime)
		msg += fmtr.format("Last Use", self.LastUse)
		msg += fmtr.format("Called", self.Called)
		msg += fmtr.format("Module Reference", "Loaded" if self.ModuleReference else "Unloaded")

		for item in dir(self.ModuleReference):
			msg += f"{item}\n"

		if self.ModuleReference:
			fmtr = "\t{:<20} {}\n"

			try:
				msg += fmtr.format("Name",self.ModuleReference.Name)
				msg += fmtr.format("Tags",self.ModuleReference.Tags)
			except Exception as err:
				msg += "Could not get module reference information"

		if not silent: print(msg)

		return msg

	# Get Plugin Name
	def Name(self):
		"""Get Name of Plugin"""

		fname = os.path.basename(self.PluginModule)
		name, ext = os.path.splitext(fname)

		return name

	# Log Plugin
	def Load(self):
		"""Load Entry, if not already Loaded"""

		if self.ModuleReference == None:
			self.LoadTime = datetime.now()
			self.ModuleReference = LoadPlugin(self.PluginModule)

	# Check To See If Module Has Been Loaded
	def IsLoaded(self):
		"""Check to see if Module Has Been Loaded"""
		return (self.ModuleReference != None)

	# Mark Plugin as Used/Referenced
	def Used(self):
		"""Mark Plugin as used"""

		self.LastUse = datetime.now()
		self.Called += 1

	# Unload Module (not functional)
	def Unload(self):
		"""Unload Module (not functional)"""
		pass

	# Unload Module By Creation Time Reference
	def UnloadCreationOlderThan(self,tdelta):
		"""Unload plugin based on creation time stamp"""

		flag = False
		diff = datetime.now() - self.CreationTime

		if diff.seconds > tdelta.seconds:
			self.Unload()
			flag = True

		return flag

	# Unload Module By Load Time Reference
	def UnloadLoadOlderThan(self,tdelta):
		"""Unload plugin based on load time stamp"""

		flag = False
		diff = datetime.now() - self.LoadTime

		if diff.seconds > tdelta.seconds:
			self.Unload()
			flag = True

		return flag

	# Unload Module By Use Time Reference
	def UnloadLoadOlderThan(self,tdelta):
		"""Unload plugin based on use time stamp"""

		flag = False
		diff = datetime.now() - self.UseTime

		if diff.seconds > tdelta.seconds:
			self.Unload()
			flag = True

		return flag

# Register Plugin
def RegisterPlugin(plugin_module,plugin_dict=None,load=False):
	"""
	Register A Plugin

	plugin_dict is an optional dictionary where the key is the plugin name
	and the value is the plugin entry.

	Returns the new plugin entry either way
	"""

	pentry = PluginEntry(plugin_module)

	if load:
		pentry.Load()

	if plugin_dict != None:
		plugin_dict[pentry.Name()] = pentry

	return pentry

# Register All Plugins in a Given Folder
def RegisterPluginsFromFolder(plugin_path,plugin_name=None,plugin_dict=None,exclude=None,load=False):
	"""Register Plugins in Given Folder"""

	plugins = dict()

	if exclude == None: exclude = [ ]

	DbgMsg(f"Registering plugins from folder {plugin_path}")

	for plugin in os.scandir(plugin_path):
		if plugin.name in exclude:
			DbgMsg(f"Excluding {plugin.name}")
			continue
		else:
			DbgMsg(f"Including {plugin.name}")

		name,ext = os.path.splitext(plugin.name)

		if re.search(r".+\.py$",plugin.name):
			name,ext = os.path.splitext(plugin.name)

			if not plugin_name or plugin_name == name:
				DbgMsg(f"Registering {plugin.path}")
				pm = RegisterPlugin(plugin.path,plugin_dict,load=load)

				if plugin_dict == None:
					plugins[pm.Name] = pm

	DbgMsg(f"Loading plugins from folder {plugin_path} completed")

	if plugin_dict != None:
		return plugin_dict

	return plugins

# Generic Plugin Execution
def RunPlugin(plugin_name,plugins,entrypoint="run",**kwargs):
	"""Generic Plugin Execution"""

	plugin = None
	result = None

	if plugin_name in plugins:
		plugin = plugins[plugin_name]

	if plugin:
		if type(plugin) is PluginEntry:
			mr = plugin.ModuleReference

			mr.run(kwargs)
		else:
			plugin.run(kwargs)

	return result

#
# User and Env Stoof
#

# Lambda for Getting the current user
CurrentUser = lambda : getpass.getuser()

#
# Webby Stoof
#

# Download Content From Web Page
def DownloadContent(url,output_filename):
	"""Download Content From URL"""

	success = True

	try:
		r = requests.get(url, allow_redirects=True)

		open(output_filename,"wb").write(r.content)
	except Exception as err:
		success = False
		ErrMsg(err,f"Could not open or save content from {url} to {output_filename}")

	return success


# Turn off Cert Errors That May Effect request completes
def TurnOffCertErrors():
	"""
	Since self signed certificates abound (and sometimes systems you re accessing over the
	web just don't have valid certs (and you are OK with that).
	This function tells urllib3 to disable certificate warnings and allow requests to
	complete.
	This is technically NOT safe NOR good eecurity practice, BUT it is sometimes necessary.
	"""
	urllib3.disable_warnings()

#
# Test Stub
#

# Test Stub
def test(args):
	CmdLineMode(True)
	DebugMode(True)

	#Msg("Currently Empty")

	def UCase(item,data=None):
		return item.upper()

	ipp = ItemProcessingPipeline(UCase,"Ucase Processor")

	breakpoint()

#
# Requisite Main Loop
#

if __name__ == "__main__":
	CmdLineMode(True)

	parser = argparse.ArgumentParser(prog="py_helper",description="py_helper")
	parser.add_argument("-t","--test",action="store_true",help="Run test stub")
	parser.add_argument("-d","--debug",action="store_true",help="Run in debug mode")
	parser.add_argument("--timestamp",action="store_true",help="Show Timestamp filters and shortcuts")

	args,unknowns = parser.parse_known_args()

	if args.debug:
		DebugMode(True)

	if args.test:
		test(args)
	elif args.timestamp:
		tsc = TimestampConverter()

		tsc.Print()
	else:
		Msg("This module was not meant for individual execution")

