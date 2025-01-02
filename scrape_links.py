import argparse
import ast
import fnmatch
import os
import pickle
import re
import unicodedata

import requests

from bs4 import BeautifulSoup

class Any:
    """
    any for many callables.
    """

    def __init__(self, funcs):
        self.funcs = funcs

    def __call__(self, arg):
        return any(func(arg) for func in self.funcs)


def wildcard_re(pattern):
    """
    Regex object from shell pattern.
    """
    return re.compile(fnmatch.translate(pattern))

def main(argv=None):
    """
    Command line interface.
    """
    parser = argparse.ArgumentParser(
        description = 'Scrape links for Akesson\'s Dialog.',
    )
    parser.add_argument(
        '--url',
        default = 'https://linusakesson.net/dialog/index.php',
        help = 'URL to scrape Linus Akesson\'s Dialog links.',
    )
    parser.add_argument(
        '--tag-name',
        default = 'a',
    )
    parser.add_argument(
        '--href',
        action = 'append',
        default = [
            '*dialog-*.zip',
            '*dialog-*.dg',
        ],
        help = 'Pattern(s) match the url.',
    )
    parser.add_argument(
        '--prepend-url',
        default = 'https:',
        help = 'Prepend this to the scraped urls.',
    )
    parser.add_argument(
        '--cache',
        default = '.dialog-cache.pickle',
        help = 'Path to save data from previous run.',
    )
    args = parser.parse_args(argv)

    url = args.url
    tag_name = args.tag_name
    prepend_url = args.prepend_url
    cache_path = args.cache

    if not args.href:
        # Match any elements having an href attribute.
        href_pattern = True
    else:
        # BeautifulSoup uses the .search method of regexes.
        href_regexes = [regex.search for regex in map(wildcard_re, args.href)]
        href_pattern = Any(href_regexes)
        del href_regexes

    dialog_items = []
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    matched = soup.find_all(tag_name, href=href_pattern)
    for element in matched:
        # URLs begin with // (slash slash)
        href = prepend_url + element['href']
        # Message for release is next to the link, wrapped by parent.
        message = element.parent.get_text()
        # Normalize special characters in the string.
        message = unicodedata.normalize('NFKC', message)
        dialog_items.append((href, message))

    # Links and messages come from <ul> in descending order of release.
    dialog_items.reverse()

    for download_url, message in dialog_items:
        print((download_url, message))

    if os.path.exists(cache_path):
        # Check for diffs
        with open(cache_path, 'rb') as cache_file:
            cache = pickle.load(cache_file)

        if cache != dialog_items:
            print('Different!')
    else:
        with open(cache_path, 'wb') as cache_file:
            pickle.dump(dialog_items, cache_file)

    # XXX
    # - Arguments from config file.
    # - Keep cache of downloaded files and git ignore them.
    # - dialog-*.zip.message files for related messages?
    # - How to know when new file comes in?
    # - How to put into the real repo?

if __name__ == '__main__':
    main()
