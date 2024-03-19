from AI.main import main
import argparse

parser = argparse.ArgumentParser()
# apparently global variables for text entries that I can't delete

parser.add_argument("link")  # nhentai link

parser.add_argument("barormosaic")  # bar or mosaic censorship
parser.add_argument("stremove")  # remove screen tones or don't
parser.add_argument("decensor_only")
args = parser.parse_args()
main(args)
