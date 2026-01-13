#!/usr/bin/env -S python #
# -*- coding: utf-8 -*-
from __future__ import absolute_import

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

__doc__ = """
Open a new serial connection to the specified port, wait 25ms, then send one or
more commands, and (unless suppressed) print the last line of the reply to each
command.
"""
try: prog = 'python -m ' + __package__
except: prog = None


import sys
import ast
import time
import argparse

if __name__ == '__main__':

	class HelpFormatter( argparse.RawDescriptionHelpFormatter ): pass	
	#class HelpFormatter( argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter ): pass
	parser = argparse.ArgumentParser( description=__doc__, formatter_class=HelpFormatter, prog=prog )
	parser.add_argument( "-t", "--timeout",           metavar='SECONDS',  type=float,  default=0.1, help='timeout in seconds' )
	parser.add_argument( "-e", "--encoding",          default='UTF8',           help='text encoding for serial input and output' )
	parser.add_argument( "-V", "--version",           action='store_true',      help='print module version and exit' )
	parser.add_argument(       "port",     nargs='?', metavar='PORT[:OPTS]',    help='port address (with optional suffix after colon, containing comma-separated Windows-derived serial options)' )
	parser.add_argument(       "commands", nargs='*', metavar='COMMANDS',       help='Keyhole command(s) (end a command with a semicolon to suppress its output)' )
	OPTS = parser.parse_args()
	
from . import Keyhole, _NORMAL_STRING, __version__

if __name__ == '__main__':

	if OPTS.__dict__.pop( 'version' ): print( __version__ ); raise SystemExit(0)
	commands = OPTS.__dict__.pop( 'commands' )
	if not commands: commands = [ '?' ]
	k = Keyhole( **OPTS.__dict__ )
	time.sleep( 0.025 )
	for command in commands:
		hush = command.strip().endswith( ';' )
		result = k( command, multiline=False if hush else 'last', raw=True )
		if not isinstance( result, _NORMAL_STRING ): result = result.decode( OPTS.encoding )
		if result.endswith( '\n' ): result = result[ :-1 ]
		if result.endswith( '\r' ): result = result[ :-1 ]
		if '_KEYHOLE_ERROR_MSG' in result:
			result = ast.literal_eval( result )
			raise SystemExit( 'from device: ' + str( result[ '_KEYHOLE_ERROR_MSG' ] ) )
		elif not hush:
			print( result )
