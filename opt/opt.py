import os
import re
import sys
import argparse
from pprint import pprint


class ArgumentsCheck(object):


    def __init__(self):
        
        args = self._build_parser()
        print args

    @staticmethod
    def _get_args(rgx, m=True):
        rgx = re.compile(rgx)
        if any(rgx.match(l) for l in sys.argv):
            return True if m else False
   
    def _build_parser(self):

        MODES = ["info", "create", "remove", "modify", "migrate", "select"]

        parser = argparse.ArgumentParser()

        parser.add_argument("mode", choices=MODES, help="Script Mode")

        glb = parser.add_argument_group("General Options")
        glb.add_argument("--sid", help="Symmetrix array ID", metavar="<S.ID>", required="select" not in sys.argv)
        glb.add_argument("-v", "--verbose", action="store_true", help="Verbose")
        glb.add_argument("--debug", action="store_true", help="Debug")
        glb.add_argument("--nop", action="store_true", help="No prompt")
        glb.add_argument("--ulun", action="store_true", help="Unbind lun")
        glb.add_argument("--nplun", action="store_true", help="Lun with no port")
        glb.add_argument("--force", action="store_true", help="Force flag")
        glb.add_argument("--no-break", action="store_true", help="No break for <--name> option")
        glb.add_argument("--size", help="Size display [cyl|mb|auto] (Df:auto)", default="auto")
        glb.add_argument("--tmp-sg", help="Info|Remove temporary S.Group (Total)")
        glb.add_argument("-n", "--name", help="New name", required=self._get_args("--(remote-)?new-(sg|mv)"))
        
        dev = parser.add_argument_group("Device Options")
        dev = dev.add_mutually_exclusive_group(required=self._get_args("select|create", False))
        dev.add_argument("-l", "--lun", help="Lun(s) ID", metavar="<L.ID>")
        dev.add_argument("-u", "--lun-uid", help="Lun(s) Unique ID (UID)", metavar="<L.UID>")
        dev.add_argument("-s", "--sg", help="Storage Group(s) (SG)", metavar="<S.Group>")
        dev.add_argument("-w", "--login", help="Login(s) (WWN)", metavar="<Login>")

        inf = parser.add_argument_group("Info Options")
        inf.add_argument("-o", "--only", action="store_true", help="Display only device info")
        
        crt = parser.add_argument_group("Create Options")
        crt.add_argument("--new-sg", action="store_true", help="Create new S.Group")
        crt.add_argument("--new-lun", help="Create new Lun(s)")
        crt.add_argument("--new-mv", help="Create new M.View")
        crt.add_argument("--node", help="Node Count (Df:1)", default=1)
        
        rmv = parser.add_argument_group("Remove Options")
        rmv = rmv.add_mutually_exclusive_group()
        rmv.add_argument("-t", "--total", action="store_true", help="Total remove")
        rmv.add_argument("-r", "--repli", action="store_true", help="Remove only replication")
        
        mig = parser.add_argument_group("Migrate Options")
        mig.add_argument("--mig-type", help="Migration Type [clone|vlun|srdf]")
        mig.add_argument("--remote-sid", help="Remote Symmetrix array ID")
        
        mig = mig.add_mutually_exclusive_group(required="migrate" in sys.argv)
        mig.add_argument("--remote-new-sg", action="store_true", help="Create new remote S.Group")
        mig.add_argument("--remote-sg", help="Remote S.Group")
        mig.add_argument("--remote-lun", help="Remote Lun(s)")
        
        mod = parser.add_argument_group("Modify Options")
        mod.add_argument("--flag", help="Flag to Modify [bcv|srdf]")
        
        args = parser.parse_args()
     
        self._check_param_dependency(parser, args)

        return args

 
    @staticmethod 
    def _check_param_dependency(parser, args):
 
        if args.mode == "create":
         
            if args.new_sg and args.sg:
                parser.error('You can create a new SG or a existing SG. Not both')

            if not args.new_sg and not args.sg:
                parser.error('Enter existing or new SG with create mode')

ArgumentsCheck()
