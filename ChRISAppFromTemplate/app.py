from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from importlib.metadata import Distribution
import requests
import json
import time
from os.path import exists
from chris_plugin import chris_plugin

__pkg = Distribution.from_name(__package__)
__version__ = __pkg.version


DISPLAY_TITLE = r"""
Random Cards
"""


parser = ArgumentParser(description='cli description',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-n', '--name', default='foo',
                    help='argument which sets example output file name')
parser.add_argument('-V', '--version', action='version',
                    version=f'%(prog)s {__version__}')


# documentation: https://fnndsc.github.io/chris_plugin/chris_plugin.html#chris_plugin
@chris_plugin(
    parser=parser,
    title='Test ChRIS Plugin',
    category='',                 # ref. https://chrisstore.co/plugins
    min_memory_limit='100Mi',    # supported units: Mi, Gi
    min_cpu_limit='1000m',       # millicores, e.g. "1000m" = 1 CPU core
    min_gpu_limit=0              # set min_gpu_limit=1 to enable GPU
)
def main(options: Namespace, outputdir: Path):
    """
    :param options: non-positional arguments parsed by the parser given to @chris_plugin
    :param inputdir: directory containing input files (read-only)
    :param outputdir: directory where to write output files
    """

    print(DISPLAY_TITLE)

    
    if not exists(str(outputdir)+"/random_cards.json"):
        random_cards = []
        for i in range(10):
            random_card = requests.get('https://db.ygoprodeck.com/api/v7/randomcard.php')
            random_cards.append(random_card.json())
            
        # Get each random card stored as a single line in the json file    
        json_cards = "\n".join([json.dumps(random_card) for random_card in random_cards])

        # Save the random card jsons to a file in the specified directory
        with open(str(outputdir)+"/random_cards.json", "w") as f:
            f.write(json_cards)

if __name__ == '__main__':
    main()
