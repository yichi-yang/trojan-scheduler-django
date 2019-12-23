import requests
from bs4 import BeautifulSoup
import re
import datetime
from django.conf import settings


class ScrapedSection:
    def __init__(self, section_id, section_type, registered, instructor, location, time, days):
        self.section_id = int(re.match("\d+", section_id).group(0))
        self.section_type = section_type
        self.need_clearance = 'D' in section_id or 'd' in section_id
        self.registered = registered
        self.instructor = instructor
        self.location = location

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
            self.start = start
            self.end = end
        else:
            self.start = self.end = None

        self.days = []
        day_names = ["M", "Tue", "W", "Thu", "F", "Sat", "Sun"]
        for i in range(len(day_names)):
            if day_names[i] in days:
                self.days.append(i)


class ScrapedCourse:
    def __init__(self, term, name):
        self.term = term
        self.name = name

    def add_section(self, section):
        setattr(self, str(section.section_id), section)


def fetch_class(term, course_name):

    url = settings.USC_SOC_URL.format(term=term, course=course_name)

    try:
        response = requests.get(url, timeout=settings.USC_SOC_TIMEOUT)
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.Timeout:
        return None

    if response:
        soup = BeautifulSoup(response.text, "html.parser")

        course_title = soup.find("h3", class_="single")
        chosen_major = soup.select_one('option[selected="selected"]')
        section_trs = soup.select("tr[data-section-id]")

        if not section_trs:
            return None

        if not chosen_major or not chosen_major.attrs.get('value'):
            return None
        major_code = chosen_major.attrs.get('value').upper()

        if not course_title:
            return None
        match = re.compile(
            r'[a-zA-Z ]+(\d+[a-zA-Z]*):').match(course_title.get_text())
        if match:
            course_code = match.group(1)
        else:
            return None

        course = ScrapedCourse(term, major_code + '-' + course_code)

        for section_tr in section_trs:
            section_id = section_tr.find("td", class_="section").get_text()
            section_type = section_tr.find("td", class_="type").get_text()
            time = section_tr.find("td", class_="time").get_text()
            days = section_tr.find("td", class_="days").get_text()
            registered = section_tr.find("td", class_="registered").get_text()
            instructor = section_tr.find("td", class_="instructor").get_text()
            location = section_tr.find("td", class_="location").get_text()

            section = ScrapedSection(
                section_id, section_type, registered, instructor, location, time, days)

            course.add_section(section)

        return course
    else:
        return None


if __name__ == '__main__':
    settings.configure(
        USC_SOC_URL='https://classes.usc.edu/term-{term}/classes/{course}',
        USC_SOC_TIMEOUT=5)
    cs201 = fetch_class('20193', 'csci-20100')
    print(cs201)
