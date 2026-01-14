import argparse as ap
import shutil
import logging
import os
import sys

from sandlerprops.cli import cli as props_cli
from sandlersteam.cli import cli as steam_cli
from sandlercubics.cli import cli as cubics_cli
from sandlercorrespondingstates.cli import cli as cs_cli
from sandlerchemeq.cli import cli as chemeq_cli

from . import versions

banner = """ 
╔════════════════════════════════════════════════════════════╗
   __             __        ___  __  ___  __   __        __  
  /__`  /\  |\ | |  \ |    |__  |__)  |  /  \ /  \ |    /__` 
  .__/ /~~\ | \| |__/ |___ |___ |  \  |  \__/ \__/ |___ .__/ 
              (c) 2025, Cameron F. Abrams <cfa22@drexel.edu>
╚════════════════════════════════════════════════════════════╝
"""
for tool in ['sandlerprops', 'sandlersteam', 'sandlercubics', 'sandlercorrespondingstates', 'sandlermisc', 'sandlerchemeq']:
    banner += f'\n  {tool:>26s} {versions[tool]}'

class ConditionalBannerFormatter(ap.RawDescriptionHelpFormatter):
    def format_help(self):
        help_text = super().format_help()
        
        # Split to extract parts
        parts = help_text.split('\n\n', 2)
        
        if len(parts) >= 2:
            usage = parts[0]  # "usage: ..."
            description = parts[1]
            rest = parts[2] if len(parts) > 2 else ''
            
            # Rearrange: banner + description + usage + rest
            result = []
            if '--no-banner' not in sys.argv:
                result.append(banner)
            result.extend([description, usage, rest])
            return '\n\n'.join(result)
        
        # Fallback
        if '--no-banner' not in sys.argv:
            return banner + '\n' + help_text
        return help_text

logger = logging.getLogger(__name__)
def setup_logging(args):    
    loglevel_numeric = getattr(logging, args.logging_level.upper())
    if args.log:
        if os.path.exists(args.log):
            shutil.copyfile(args.log, args.log+'.bak')
        logging.basicConfig(filename=args.log,
                            filemode='w',
                            format='%(asctime)s %(name)s %(message)s',
                            level=loglevel_numeric
        )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s> %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def cli():
    subcommands = {
        'props': dict(
            func = props_cli,
            help = 'query and manipulate thermophysical property data'
        ),
        'cubic': dict(
            func = cubics_cli,
            help = 'query and manipulate cubic equation of state calculations'
        ),
        'steam': dict(
            func = steam_cli,
            help = 'work with steam tables and properties of water/steam'
        ),
        'cs': dict(
            func = cs_cli,
            help = 'work with corresponding states calculations'
        ),
        'chemeq': dict(
            func = chemeq_cli,
            help = 'work with chemical equilibrium calculations'
        ),
    }
    parser = ap.ArgumentParser(
        description="Sandlertools: A collection of computational tools based on Chemical, Biochemical, and Engineering Thermodynamics (5th edition) by Stan Sandler",
        formatter_class = ConditionalBannerFormatter,
        epilog="(c) 2025, Cameron F. Abrams <cfa22@drexel.edu>")
        
    parser.add_argument(
        '-b',
        '--banner',
        default=True,
        action=ap.BooleanOptionalAction,
        help='toggle banner message'
    )
    parser.add_argument(
        '--logging-level',
        type=str,
        default='debug',
        choices=[None, 'info', 'debug', 'warning'],
        help='Logging level for messages written to diagnostic log'
    )
    parser.add_argument(
        '-l',
        '--log',
        type=str,
        default='', # no log file by default
        help='File to which diagnostic log messages are written'
    )
    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="command",
        metavar="<command>",
        required=True,
    )
    command_parsers={}
    for k, specs in subcommands.items():
        command_parsers[k] = subparsers.add_parser(
            k,
            help=specs['help'],
            formatter_class=ap.RawDescriptionHelpFormatter,
            add_help=False
        )
        command_parsers[k].set_defaults(func=specs['func'])

    args, remaining = parser.parse_known_args()
    sys.argv = [f'sandlertools-{args.command}'] + remaining
    if hasattr(args, 'func'):
        setup_logging(args)
        args.func()
        print('Thanks for using sandlertools!')
    else:
        my_list = ', '.join(list(subcommands.keys()))
        print(f'No subcommand found. Expected one of {my_list}')