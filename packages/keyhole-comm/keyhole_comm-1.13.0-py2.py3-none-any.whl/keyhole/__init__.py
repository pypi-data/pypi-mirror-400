#!/usr/bin/env -S python #
# -*- coding: utf-8 -*-

# $BEGIN_KEYHOLE_LICENSE$
# 
# This file is part of the Keyhole project, a lightweight library for the
# Arduino IDE, for interpreting commands and communicating variable values via
# a JSON- and Python-compatible text interface. 
# 
# Author: Jeremy Hill (2023-)
# Development was supported by the NIH, NYS SCIRB, Veterans Affairs RRD,
# and the Stratton VA Medical Center.
# 
# No Copyright
# ============
# The author has dedicated this work to the public domain under the terms of
# Creative Commons' CC0 1.0 Universal legal code, waiving all of his rights to
# the work worldwide under copyright law, including all related and neighboring
# rights, to the extent allowed by law.
# 
# You can copy, modify, distribute and perform the work, even for commercial
# purposes, all without asking permission. See Other Information below.
# 
# Other Information
# =================
# In no way are the patent or trademark rights of any person affected by CC0,
# nor are the rights that other persons may have in the work or in how the work
# is used, such as publicity or privacy rights.
# 
# The author makes no warranties about the work, and disclaims liability for
# all uses of the work, to the fullest extent permitted by applicable law. When
# using or citing the work, you are requested to preserve the author attribution
# and this copyright waiver, but you should not imply endorsement by the author.
# 
# $END_KEYHOLE_LICENSE$

"""
Provides the `Keyhole` class and attendant exception classes,
for simple line-by-line serial-port communication (especially
with microcontrollers that have been programmed using the
Keyhole library for the Arduino IDE).
"""

__version__ = '1.13.0'

__all__ = [
	'Keyhole',
	'KeyholeError', 'KeyholeVariableError', 'KeyholeValueError', 
	'KEOF',
]

from ast import literal_eval
try:    from time import perf_counter as clock
except: from time import clock
import glob

import serial # python -m pip install pyserial

try: from BCI2000Tools.Container import Bunch as Container # optional nice-to-have, but don't worry if it's not there
except: Container = dict

class KeyholeError( Exception ): pass
class KeyholeVariableError( AttributeError, KeyholeError ): pass
class KeyholeValueError( ValueError, KeyholeError ): pass
class KEOF: pass
KEOF = KEOF()

_NORMAL_STRING = type( '' )
_RAW_BYTES = type( ''.encode( 'utf8' ) )
_ENCODED_STRING = type( ''.encode( 'utf8' ).decode( 'utf8' ) )

class Keyhole( object ):
	r"""
	Connect to a serial device using the same constructor arguments
	as `serial.Serial`::
	
	    k = Keyhole('COM4')
	
	Send a message using the `<<` operator. If the message is not
	already raw `bytes`, it will be automatically encoded to `bytes`
	and a newline will be appended if there wasn't one already::
	
	    k << 'hello'     # sends b'hello\n'
	
	Equivalently, you call the instance with the message as the
	argument::
	
	    k('hello')       # sends b'hello\n'
	    k()              # sends b'?\n' by default
	
	Whichever syntax you use, the return value will provide information
	from the first line of any reply that occurs within the timeout
	period (decoded into a `dict`, if the line was a valid `dict`
	literal) along with timing information.
	
	If the recipient of the message is a microcontroller that has
	has been programmed using the Keyhole library for the Arduino IDE,
	and it exposes variables via a Keyhole, then these variables can
	be accessed as attributes::
	
	    print(k.foo)
	    k.foo = 123
	
	and `k()` will give you a complete record of the variables and
	their values. 
	
	To close the connection, `k<<KEOF` or `k<<None` or `k._close()`
	will all work (this will also happen automatically when `k` is
	garbage-collected).	
	"""
	def __init__( self, port, timeout=0.1, encoding='UTF8', **kwargs ):
		"""
		All valid `serial.SerialBase` constructor args can be used,
		plus the additional argument `encoding` which determines how
		the Keyhole encodes/decodes between characters and raw bytes.
		"""
		# Windows-derived suffix format:
		# 
		#     COMx[:][baud={19200},][parity={n|e|o|m|s},][data={5|6|7|8},][stop={1|1.5|2},][dtr={on|off|hs},][rts={on|off|hs|tg},]
		#            [to={on|off},][xon={on|off},][odsr={on|off},][octs={on|off},][idsr={on|off},]
		# 
		# corresponding `serial.SerialBase` **kwargs and their defaults:
		#         baudrate=9600, parity='N', bytesize=8, stopbits=1, dsrdtr=False, rtscts=False, xonxoff=False
		# 
		# NB:
		# * there's no translation for `idsr=...` (DSR sensitivity / gating receive based on DSR, a DCB feature with no direct equivalent in `serial.SerialBase( **kwargs )` ).
		# * there's no translation for `to=...` (instead, specify timeout behavior by setting the `timeout` argument to 0 or `None` or a number of seconds)
		# * there's no support for `rts=tg` (RTS toggle)
		# * `dtr=hs` and `rts=hs` correspond to `dsrdtr=True` and `rtscts=True` respectively
		# * `dtr={on|off}` and `rts={on|off}` have no direct equivalent as constructor `**kwargs` but are supported as posthoc manipulations (after the port is open)
		# * actual explicitly-supplied `**kwargs` will override corresponding options in the suffix

		suffix = ''
		posthoc = {}
		if ':' in port: port, suffix = port.split( ':', 1 )
		suffix = suffix.strip().split( ',' ) if suffix.strip() else []
		for key in [ 'dtr', 'rts' ]:
			if key in kwargs:
				value = kwargs.pop( key )
				suffix.append( '%s=%s' % ( key, value ) )
		translations = dict( baud='baudrate', parity='parity', data='bytesize', stop='stopbits', xon='xonxoff', odsr='dsrdtr', octs='rtscts' )
		for windowsDerivedKey, pyserialKwarg in translations.items():
			if windowsDerivedKey in kwargs and pyserialKwarg not in kwargs:
				kwargs[ pyserialKwarg ] = kwargs.pop( windowsDerivedKey )
		for item in suffix:
			if '=' in item: key, value = item.split( '=', 1 )
			else: key, value = item, 'on'
			key = key.strip().lower()
			key = translations.get( key, key )
			if not key: continue
			value = value.strip().upper()
			try: value = int( value )
			except:
				try: value = float( value )
				except: value = { 'ON' : True, 'TRUE' : True, 'OFF' : False, 'FALSE' : False }.get( value, value )
			if   key == 'dtr' and value == 'HS': key, value = 'dsrdtr', True
			elif key == 'rts' and value == 'HS': key, value = 'rtscts', True
			if key in kwargs:
				pass
			elif key in [ 'dtr', 'rts' ]:
				if value not in [ True, False ]: raise ValueError( 'no support for %s=%s' % ( key.lower(), value.lower() ) )
				posthoc[ key ] = value
			else:
				kwargs[ key ] = value
		if '*' in port or '?' in port or '[' in port:
			matches = glob.glob( port )
			if len( matches ) < 1: raise ValueError(       'found no matches for port=%r' % port )
			if len( matches ) > 1: raise ValueError( 'found multiple matches for port=%r' % port )
			port = matches[ 0 ]
		if timeout is not None: timeout = float( timeout )
		self.__dict__.update(
			_connection = serial.Serial( port, timeout=timeout, **kwargs ),
			_encoding  = encoding,
			_kwargs = kwargs,
			_posthoc = posthoc,
			_lastReply  = None,
		)
		for key, value in posthoc.items():
			setattr( self._connection, key, value )
		
	def _close( self ):
		"""Closes the connection. (You can also do `self<<KEOF` or `self<<None`.)"""
		return self._connection.close()
	
	def __getattr__( self, name ):
		reply = self << name
		if name in reply: return reply[ name ]
		if reply.get( '_REPLY', None ) == '': return None
		if '_KEYHOLE_ERROR_MSG' in reply or 'KEYHOLE_COMMAND_ERROR' in reply: # the latter is from an older version of the Arduino Keyhole library
			raise KeyholeVariableError( 'failed to recognize %r' % name )
		raise KeyholeError( 'could not understand reply %r' % reply )
	
	def __setattr__( self, name, value ):
		reply = self << name + '=' + repr( value )
		if '_KEYHOLE_ERROR_MSG' in reply:
			errorType = reply.get( '_KEYHOLE_ERROR_TYPE', None )
			if errorType in [ 'ReadOnly' ]: raise KeyholeVariableError( reply[ '_KEYHOLE_ERROR_MSG' ] )
			if errorType in [ 'BadValue' ]: raise KeyholeValueError(    reply[ '_KEYHOLE_ERROR_MSG' ] )
			raise KeyholeVariableError( 'failed to set %r' % name )
		elif 'KEYHOLE_COMMAND_ERROR' in reply: # from an older version of the Arduino Keyhole library
			raise KeyholeVariableError( 'failed to set %r' % name )
	
	__getitem__ = __getattr__
	__setitem__ = __setattr__
		
	def _update( self, **kwargs ):
		for k, v in kwargs.items(): setattr( self, k, v )
			
	def __dir__( self ):
		reply = self() # if we're talking to the Arduino-IDE Keyhole library on the other side, this will elicit a reply detailing all exposed variables and their values, in JSON format, which Python can also interpret as a dict with literal_eval()
		return [ k for k in reply.keys() if not k.startswith( '_' ) ]
	_getAttrNames = __dir__
	
	def __iter__( self ): return self
	def __next__( self ):
		reply = self._connection.readline()
		if not reply: raise StopIteration
		if not isinstance( reply, _NORMAL_STRING ):
			reply = reply.decode( self._encoding )
		if   reply.endswith( '\r\n' ): reply = reply[ :-2 ]
		elif reply.endswith(   '\n' ): reply = reply[ :-1 ]
		return reply
		
	def __lshift__( self, command ):
		return self( command )
		
	def __call__( self, command='?', multiline=False, raw=False ):
		if command is KEOF or command is None: self._connection.close(); return Container( _CLOSED=True )
		if isinstance( command, ( _NORMAL_STRING, _ENCODED_STRING ) ):
			# In Python 3, where `_NORMAL_STRING` is the same as `_ENCODED_STRING`, you have the option of bypassing the automatic newline-termination and encoding by
			# passing a `bytes` instance explicitly. But if you pass a normal string, it get will preprocessed. In Python 2, where `_NORMAL_STRING` is the same as
			# `_RAW_BYTES`, we'll still do the preprocessing (and it will still work), so you can still do `k('foo')` without effort/thought---it's just that, under
			#  Python 2, the `k(cmd)` or `k << cmd` shortcuts don't give you the "advanced" option of sending raw bytes explicitly and having them forwarded un-preprocessed.
			command = ( command.rstrip( '\n' ) + '\n' ).encode( self._encoding )
		if not isinstance( command, _RAW_BYTES ):
			raise ValueError( 'cannot send %s instances, only strings' % command.__class__.__name__ )
		write = self._connection.write
		flush = self._connection.flushOutput
		read  = self._connection.readline		
		
		########
		t0 = clock()
		write( command )
		flush()
		reply = read()
		if multiline:
			collated = reply[ :0 ]
			while reply:
				if multiline == 'last': collated = reply
				else: collated += reply
				reply = read()
			reply = collated
		elapsedMilliseconds = ( clock() - t0 ) * 1000
		########
		if raw: return reply
		if not isinstance( reply, _NORMAL_STRING ):
			reply = reply.decode( self._encoding )
		if reply.strip().startswith( '{' ):
			try:    reply = Container( literal_eval( reply ) )
			except: reply = Container( _REPLY=reply )
		else:
			reply = Container( _REPLY=reply )
		reply[ '_ELAPSED_MS' ] = elapsedMilliseconds
		self.__dict__.update( _lastReply=reply )
		return reply
		
if _NORMAL_STRING is _RAW_BYTES: Keyhole.next = Keyhole.__next__ # Python 2 compatibility
	
if __name__ == '__main__':
	import sys
	args = sys.argv[ 1: ]
	if not args: args.append( 'COM7' )
	k = Keyhole( *args )
	print( k() )
