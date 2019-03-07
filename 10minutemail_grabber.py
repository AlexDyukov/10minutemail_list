#!/usr/bin/env python3

# install dependencies before use:
# pip3 install selenium tldextract

import re
import tldextract
import pickle
from sys import stderr
from time import sleep, time
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException


def _get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver


def get_body(url, class_name, wait_timeout):
    driver = _get_driver()

    try:
        # get page
        driver.get(url)

        # wait for key element
        sleep(1)
        WebDriverWait(driver, wait_timeout).until(lambda x: x.find_element_by_class_name(class_name))
    except TimeoutException:
        print('We got an error while processing {}'.format(url), file=stderr)
        return ''

    # get body
    body = driver.find_element_by_tag_name('body').get_attribute('innerHTML')

    driver.close()
    return body


def _cleanup_html(html):
    # trim any spaces
    clean_html = re.sub(r'\s+', ' ', html.strip())

    # lower any characters, because DNS system ignore cases
    clean_html = clean_html.lower()

    # remove comments, because invisible
    clean_html = re.sub(r'(<!--)(.*?)(-->)', '', clean_html)

    # remove scripts parts, because invisible
    clean_html = re.sub(r'(<script)(.*?)(<\/script>)', '', clean_html)

    return clean_html


def find_domains(html):
    text = _cleanup_html(html)

    # find words looks like domains, but not urls
    domain_re = r'([\s\>\"\'\@]([\w]+([\-]{1,2}\w+)*\.)+\w+([\-]{1,2}\w+)*)'
    possible_domains = [x[0] for x in re.findall(domain_re, text)]

    # parse words to domains
    domains = set([tldextract.extract(d[1:]).registered_domain for d in possible_domains])

    return domains


def get_uniq_domains(list_of_domainsset):
    result = set()
    for domainsset in list_of_domainsset:
        lods = list_of_domainsset.copy()
        lods.remove(domainsset)
        for domain in domainsset:
            if all([domain not in ds for ds in lods]):
                result.add(domain)

    return result


def update_state(domains, expire_time):
    state = {}
    state_file = 'state.dump'
    try:
        with open(state_file, 'rb') as f:
            state = pickle.load(f)
    except (IOError, EOFError):
        pass

    current_time = time()
    for d in domains:
        state[d] = current_time

    state = {domain: time for (domain, time) in state.items() if current_time - time < expire_time}
    with open(state_file, 'wb') as f:
        pickle.dump(state, f)

    return state.keys()


def main():
    wait_timeout = 10
    expire_time = 2629800  # month

    # TODO: http://email-wegwerf.de/wegwerfemail-liste.html
    parse_list = [('https://dropmail.me/en/', 'email'),
                  ('https://10minutemail.net/', 'mailtext'),
                  ('https://10minutemail.com/10MinuteMail/index.html?dswid=' + str(randint(-16383, 16384)), 'mail-address-address'),
                  ('http://15qm.com/?act=sevin', 'getButton'),
                  ('https://www.crazymailing.com/', 'crazy-mail'),
                  ('https://tempr.email/about.htm', 'List'),
                  ('http://www.fakemailgenerator.com/', 'input-group-btn'),
                  ('https://freeola.com/freeola500/full-free-email-addresses.php', 'griddy')]

    parsed_bad_domains = []
    for (url, key) in parse_list:
        # <head> doesn't have visible parts
        body = get_body(url, key, wait_timeout)
        domains_like = find_domains(body)
        parsed_bad_domains.append(domains_like)

    # no need to grab, because static
    parsed_bad_domains.append({'10minutemail.co.uk', '10minutenemail.de', '20minutemail.com',
                               '20mail.it', '20mail.in', '20email.eu', 'anonmails.de',
                               'bspamfree.org', 'byom.de', 'trashmail.org', 'vermutlich.net',
                               'wegwerf-email.at', 'cookiecooker.de', 'dispostable.com',
                               'spoofmail.de', 'candymail.de', 'funnymail.de', 'squizzy.net',
                               'emailgo.de', 'wegwerfemail.de', 'sofort-mail.de', 'tempmailer.com'
                               'trashmail.de', 'mailcatch.com', 'mt2015.com'})

    bl_domains = get_uniq_domains(parsed_bad_domains)
    bl_domains = update_state(bl_domains, expire_time)
    print('\n'.join(bl_domains))


if __name__ == '__main__':
    main()
