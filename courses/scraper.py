import requests
from bs4 import BeautifulSoup
import re
import datetime
from django.conf import settings

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def make_section_dict(section_id, section_type, registered, instructor, location, time, days):

    section = {}

    section['section_id'] = int(re.match("\d+", section_id).group(0))
    section['section_type'] = section_type
    section['need_clearance'] = 'D' in section_id or 'd' in section_id
    section['registered'] = registered
    section['instructor'] = instructor
    section['location'] = location

    match = re.compile(r'(\d+):(\d+)-(\d+):(\d+)(am|pm)').match(time)

    if(match):
        start = datetime.time(hour=int(match.group(1)),
                              minute=int(match.group(2)))
        end = datetime.time(hour=int(match.group(3)),
                            minute=int(match.group(4)))
        if match.group(5) == 'pm':
            start_hour = start.hour + 12 if start.hour < 12 else start.hour
            end_hour = end.hour + 12 if end.hour < 12 else end.hour
            if start_hour > end_hour:
                start_hour -= 12
            start = start.replace(hour=start_hour)
            end = end.replace(hour=end_hour)
        section['start'] = start
        section['end'] = end
    else:
        section['start'] = section['end'] = None

    section['days'] = []
    day_names = ["M", "Tue", "W", "Thu", "F", "Sat", "Sun"]
    for i in range(len(day_names)):
        if day_names[i] in days:
            section['days'].append(i)

    return section


def fetch_class(term, course_name):

    logger.info('Fetch {term} {course}'.format(term=term, course=course_name))

    url = settings.USC_SOC_SCRAPER_URL.format(term=term, course=course_name)

    try:
        response = requests.get(url, timeout=settings.USC_SOC_SCRAPER_TIMEOUT)
    except requests.exceptions.ConnectionError:
        logger.warning('{term} {course} | Connection error'.format(
            term=term, course=course_name))
        return None
    except requests.exceptions.Timeout:
        logger.warning('{term} {course} | Timeout'.format(
            term=term, course=course_name))
        return None

    if response:
        soup = BeautifulSoup(response.text, "html.parser")

        section_trs = soup.select("tr[data-section-id]")
        section_url = soup.select_one('td.info a.lightbox')

        if not section_trs:
            logger.info('{term} {course} | No sections found'.format(
                term=term, course=course_name))
            return None

        if not section_url or not section_url.attrs.get('href'):
            logger.warning(
                '{term} {course} | No section-url found'.format(term=term, course=course_name))
            return None
        match = re.compile(
            r'https:\/\/classes\.usc\.edu\/term-(\d+)\/section\/([a-zA-Z0-9-]+)\/').match(section_url.attrs.get('href'))
        if match:
            real_term = match.group(1)
            real_name = match.group(2).lower()
            if term != real_term or course_name != real_name:
                logger.warning('{term} {course} does not match fetched data: {r_term} {r_name}'.format(
                    term=term, course=course_name, r_term=real_term, r_name=real_name))
        else:
            logger.warning(
                '{term} {course} | No match in section-url'.format(term=term, course=course_name))
            return None

        course = {"term": real_term, "name": real_name, "sections": []}

        for section_tr in section_trs:
            section_id = section_tr.find("td", class_="section").get_text()
            section_type = section_tr.find("td", class_="type").get_text()
            time = section_tr.find("td", class_="time").get_text()
            days = section_tr.find("td", class_="days").get_text()
            registered = section_tr.find("td", class_="registered").get_text()
            instructor = section_tr.find("td", class_="instructor").get_text()
            location = section_tr.find("td", class_="location").get_text()

            section = make_section_dict(
                section_id, section_type, registered, instructor, location, time, days)

            course['sections'].append(section)

        return course
    else:
        logger.warning('{term} {course} | No response'.format(
            term=term, course=course_name))
        return None
