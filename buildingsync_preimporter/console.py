#!/usr/bin/env python3

import argparse

def extract():
	print("hi extract function")

def main():

  # Construct Parsers
  parser = argparse.ArgumentParser(description='Tool for extracting assets data from BuildingSync files')
  subparsers = parser.add_subparsers()
  parser_extract = subparsers.add_parser('extract', description='Command for extracting data')
  parser_extract.add_argument(
    'xml',
    metavar='xml',
    type=str,
    help='buildingsync file to use'
  )
  parser_extract.set_defaults(func=extract)
  # command with no sub-commands should just print help
  parser.set_defaults(func=lambda _: parser.print_help())

  args = parser.parse_args()
  args.func(args)
 
  print("hello buildingsync_preimport")

if __name__ == "__main__":
  main()