# -*- coding: UTF-8 -*-
import mechanize

from bs4 import BeautifulSoup
from datetime import datetime

from django.db.models.query_utils import Q

from metadata.models import TanitJobsCategory
from annonce.models import Offer


class TanitJobs(object):
    def __init__(self, model):
        self.offer = {}
        self.url = "http://tanitjobs.com/search-results-jobs/?action=search&listings_per_page=100&view=list"
        self.model = model
        self.job_prefix = 'http://tanitjobs.com/display-job/'
        self.company_prefix = 'http://tanitjobs.com/company/'
        self.browser = mechanize.Browser()

    def get_html_text(self, url=None):
        self.browser.set_handle_robots(False)
        self.browser.addheaders = [('User-agent', 'Mozilla')]
        if url:
            return self.browser.open(url)
        return self.browser.open(self.url)

    def get_soup(self, url=None):
        return BeautifulSoup(self.get_html_text(url), "lxml")

    def get_offer_details(self, table, token):
        self.offer = {'job_title': " ".join(table.find('h2').text.split()), 'lieu': '', 'token': token,
                      'expired_at': '', 'sector_activity_other': '', 'description': '', 'sector_activity': [],
                      'company_picture': '', 'company_name': '', 'company_address': '', 'company_url': ''}
        # Here we get the title of each block
        blocks = table.findAll('h3')
        # we loop in each block to get the description/text
        for block in blocks:
            if 'Secteur ' in block.text:
                for sector in "".join(block.next_sibling.split()).split(','):
                    qs = TanitJobsCategory.objects.filter(name__exact=sector)
                    for obj in qs:
                        self.offer['sector_activity'].append(obj)
                self.offer['sector_activity_other'] = " ".join(block.next_sibling.split())
            if 'Lieu' in block.text:
                try:
                    self.offer['lieu'] = "".join(block.parent.div.text.split()).lower().title()
                except AttributeError:
                    pass
            if 'Expire le' in block.text:
                if len(block.parent.text.replace('Expire le : ', '').split()) == 1:
                    self.offer['expired_at'] = datetime.strptime(" ".join(block.parent.text.replace('Expire le : ',
                                                                                                    '').split()),
                                                                 '%Y-%m-%d')
            for p in block.findAllNext('p'):
                if p.findAllPrevious('h3')[0].text == block.text:
                    self.offer['description'] += u''.join(p.text.strip())
        # Here we get the picture of the company
        company_img = table.find('img')
        if company_img:
            self.offer['company_picture'] = company_img['src']
        print self.offer
        return self.offer

    def get_offer(self, obj, tokens):
        job = obj.find('a', attrs={"class": "title_offre"})
        company = obj.find('a', id="companytitle")
        company_url = ''
        if company:
            company_url = company['href']
        if job:
            job_url = job['href']
            job_token = job_url.replace(self.job_prefix, '').split('/')[0]
            if str(job_token) not in tokens:
                table = self.get_soup(job_url.encode('utf-8')).find('table', attrs={"class": "display_job"})
                offer_details = self.get_offer_details(table, job_token)
                if company_url.startswith(self.company_prefix):
                    offer_details['company_url'] = company_url
                    offer_details['company_token'] = company_url.replace(self.company_prefix, '').split('/')[0]
                return offer_details
        return {}

    def get_tokens(self):
        return [obj['token'] for obj in self.model.objects.values('token') if obj['token']]

    def get_pages(self):
        pages = self.get_soup().find_all("span", attrs={"class": "navigationItems"})
        items = pages[0].find_all('li')
        return int(items[-1:][0].a.text)

    def get_or_create_jobs(self):
        tokens = self.get_tokens()
        pages = range(1, self.get_pages() + 1)
        all_objects = []
        for page in pages:
            print '---------------- Page ' + str(page) + '--------------------'
            url = self.url + '&page=' + str(page)
            objects = self.get_soup(url).find_all("div", attrs={"class": "offre-emploi"})
            for obj in objects:
                offer = self.get_offer(obj, tokens)
                sectors = []
                if 'sector_activity' in offer:
                    sectors = offer['sector_activity']
                    offer.pop('sector_activity')
                if offer:
                    try:
                        self.model.objects.get(token=offer['token'])
                    except self.model.DoesNotExist:
                        instance = self.model(**offer)
                        instance.save()
                        instance.sector_activity.add(*sectors)
                        instance.save()
                        # self.model.objects.bulk_create([self.model(**self.get_offer(obj, tokens)) for obj in objects])
                        # all_objects += [self.model(**self.get_offer(obj, tokens)) for obj in objects]
        return all_objects


def get_jobs():
    # import new jobs
    tanit = TanitJobs(model=Offer)
    # Clear old jobs
    # Offer.objects.filter(Q(expired_at__lt=datetime.now()) | Q(token__isnull=True)).delete()
    # Import New Jobs
    tanit.get_or_create_jobs()
