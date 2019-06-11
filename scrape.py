import logging
import os
import re
import sys
import mechanize

from datetime import datetime
from datetime import timedelta

baseurl = "http://ratsinfo.roesrath.de"

basepath = "/ratsinfo/roesrath"

meetings_url = "%s%s/Meeting.html" % (baseurl, basepath)

documents_path = os.getenv('DOCUMENTS_PATH', default='./documents')

# scraper start date for the meeting calendar
start = datetime(2006, 2, 1, 0, 0, 0)

def collect_meetings(year, month):
    """
    Collects info on meetings, for a month.
    Note: Month is a number between 0 and 11.
    """
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.open(meetings_url + "?month=%s&year=%s" % (month, year))

    regex = "%s/Meeting.html" % basepath

    for link in browser.links(url_regex=regex):

        if "&mid=" in link.url:
            collect_documents_from_meeting(browser, link.url)


def collect_documents_from_meeting(browser, url):
    """
    Collects info on documents handled in meetings,
    given a meeting URL
    """
    browser.open(url)
    print(browser.title())

    # ensure each URL is only handled once
    urls = set()

    regex = "%s/Proposal.html" % basepath

    for link in browser.links(url_regex=regex):
        print(link)
        urls.add(link.url)
    
    for url in urls:
        get_document(browser, url)


def get_document(browser, url):
    """
    Fetches a single document
    """
    browser.open(url)
    print("\nDokumentendetails:", browser.title(), url)

    regex1 = "%s/[0-9]+/" % basepath
    regex2 = "%s/([0-9]+)/" % basepath

    for link in browser.links(url_regex=regex1):
        print(link.url)
        match = re.match(regex2, link.url)
        if match is not None:
            filename, headers = browser.retrieve(baseurl + link.url)

            target_path = os.path.join(documents_path, match.group(1))
            os.makedirs(target_path, exist_ok=True)

            disp = headers["Content-Disposition"]
            match2 = re.search('filename="([^"]+)"', disp)
            if match2 is not None:
                os.rename(filename, target_path + "/" + match2.group(1))
            else:
                print(match2)
                print("Error: could not retrieve target file name form headers - %s" % disp)


if __name__ == "__main__":
    # collect 3 years back and 100 days forward
    now = datetime.now()
    end = now + timedelta(days=100)
    date = start
    lastmonth = None

    while date < end:
        date += timedelta(days=1)
        year = datetime.strftime(date, "%Y")
        month = int(datetime.strftime(date, "%m")) - 1
        
        if month != lastmonth:
            print(year, month)
            lastmonth = month

            collect_meetings(year, month)
