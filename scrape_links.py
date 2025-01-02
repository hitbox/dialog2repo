import argparse
import ast
import configparser
import fnmatch
import os
import pickle
import re
import unicodedata

import certifi
import requests

from bs4 import BeautifulSoup

app_name = 'scrape_links'
environ_config_key = 'SCRAPE_LINKS_CONFIG'

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
    # Detect config path and use them as defaults for the argument parser.
    config = configparser.ConfigParser()
    if environ_config_key in os.environ:
        config.read(os.environ[environ_config_key])

    default_url = config.get(app_name, 'url', fallback=None)
    default_tag_name = config.get(app_name, 'tag-name', fallback=None)
    default_href = []
    if config.has_section(app_name):
        for key in config[app_name]:
            if key.startswith('href') and key[4:].isdigit():
                default_href.append(wildcard_re(config[app_name][key]))
    default_prepend_url = config.get(app_name, 'prepend-url', fallback=None)

    parser = argparse.ArgumentParser(
        description = 'Scrape links for Akesson\'s Dialog.',
        epilog =
            'Config path found in SCRAPE_LINKS_CONFIG environment variable.',
    )
    parser.add_argument(
        '--url',
        default = default_url,
        help = 'URL to scrape Linus Akesson\'s Dialog links. Default: %(default)s',
    )
    parser.add_argument(
        '--tag-name',
        default = default_tag_name,
        help = 'HTML element tag to look for. Default: %(default)r',
    )
    parser.add_argument(
        '--href',
        action = 'append',
        default = default_href,
        type = wildcard_re,
        help = 'Pattern(s) match the url. Default: %(default)s',
    )
    parser.add_argument(
        '--prepend-url',
        default = default_prepend_url,
        help = 'Prepend this to the scraped urls. Default: %(default)s',
    )
    args = parser.parse_args(argv)

    url = args.url
    tag_name = args.tag_name
    prepend_url = args.prepend_url

    if not args.href:
        # Match any elements having an href attribute.
        href_pattern = True
    else:
        # BeautifulSoup uses the .search method of regexes.
        href_pattern = Any([regex.search for regex in args.href])

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

if __name__ == '__main__':
    main()
