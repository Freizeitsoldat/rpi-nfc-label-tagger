import os.path
import signal
import sys
from argparse import ArgumentParser
from traceback import print_exc
import nfc
import ndef

def main():
    # default to debug to catch unexpected exceptions during setup
    debug = True

    # Getting the arguments
    try:
        parser = ArgumentParser()
        parser.add_argument(
            '-d', '--debug',
            dest='debug',
            default=False,
            action='store_true',
            help='debug mode (be more verbose and print tracebacks)')
        parser.add_argument(
            '-u', '--url',
            dest='url',
            default=True,
            help='url')
        parser.add_argument(
            '-i', '--id',
            dest='uuid',
            default=True,
            help='uuid')
        parser.add_argument(
            '-t', '--title',
            dest='title',
            default=True,
            help='title')
        args = parser.parse_args()

        # Update debug
        debug = args.debug
        if debug == True:
            print args

        # Write data to the tag
        clf = nfc.ContactlessFrontend('usb:001:004')
        tag = clf.connect(rdwr={'on-connect': lambda tag: False, 'lto': 60000})
        beaconuid = str(tag.identifier).encode("hex")
        tag.ndef.records = [ndef.SmartposterRecord(args.url +"?uuid="+args.uuid, args.title)]

        # Return
        if tag.ndef.has_changed == False:
            return 0
        else:
            return 1


    except Exception as e:
        sys.stderr.write("An error occured: " + repr(e) + "\n")
        if debug:
            print_exc(e)
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
