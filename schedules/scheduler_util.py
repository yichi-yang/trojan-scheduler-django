from collections import OrderedDict
import itertools
import bisect
import heapq
from datetime import datetime, time, timedelta
from .models import Schedule


class SchedulerException(Exception):
    pass


class UncaughtSchedulerException(SchedulerException):
    def __init__(self, exception, name, task, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = exception
        self.name = name
        self.task = task

    def __str__(self):
        return "{} task-{}: {}".format(self.name, self.task, self.exception.__str__())


class TimeoutException(SchedulerException):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "Scheduler timeout"


class MalformedCoursebinException(SchedulerException):
    def __init__(self, exception, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = exception

    def __str__(self):
        return self.exception.__str__()


class TimeFormatException(SchedulerException):
    def __init__(self, exception, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = exception

    def __str__(self):
        return self.exception.__str__()


def str_time2timedelta(str):
    try:
        result = datetime.combine(datetime.min,
                                  time.fromisoformat(str)) - datetime.min
    except ValueError as e:
        raise TimeFormatException(e) from e
    return result


class Section:

    def __init__(self, section_dict):
        super().__init__()
        start = section_dict.get("start")
        end = section_dict.get("end")
        self.start = str_time2timedelta(start) if start is not None else None
        self.end = str_time2timedelta(end) if end is not None else None
        self.days = section_dict.get("days")
        self.id = section_dict.get("id")
        self.exclude = section_dict.get("exclude")
        self.exempt = section_dict.get("exempt")


class Timetable:

    def __init__(self, timetable=None):
        self.timetable = [list() for i in range(7)]\
            if timetable is None else timetable

    def insert(self, day, begin, end):
        loc = bisect.bisect(self.timetable[day], (begin, end))

        # has preceding course and overlaps
        if loc - 1 >= 0 and self.timetable[day][loc - 1][1] > begin:
            return False

        # have following course and overlaps
        if loc < len(self.timetable[day]) and self.timetable[day][loc][0] < end:
            return False

        self.timetable[day].insert(loc, (begin, end))

        return True

    def clone(self):
        timetable_copy = [[*day] for day in self.timetable]
        return Timetable(timetable_copy)


class TimeSlot:
    def __init__(self, start, end, wiggle, weight):
        self.start = str_time2timedelta(start)
        self.end = str_time2timedelta(end)
        self.wiggle = str_time2timedelta(wiggle)
        self.weight = weight
        self.lower = self.start - self.wiggle
        self.upper = self.end + self.wiggle
        self.length = self.end - self.start

    def fits_in(self, break_start, break_end):
        real_start = max(self.lower, break_start)
        real_end = min(self.upper, break_end)
        if real_start > real_end:
            return False
        break_len = real_end - real_start
        return break_len >= self.length


class ResultSchedule:
    def __init__(self, sections, early_score, late_score, break_score, reserved_score):
        self.sections = sections
        self.early_score = early_score
        self.late_score = late_score
        self.break_score = break_score
        self.reserved_score = reserved_score
        self.total_score = early_score + late_score + break_score + reserved_score

    def ordering_tuple(self):
        return (self.total_score, self.reserved_score, self.early_score, self.late_score, self.break_score)

    def __lt__(self, rhs):
        if self.ordering_tuple() != rhs.ordering_tuple():
            return self.ordering_tuple() > rhs.ordering_tuple()
        return self.sections < rhs.sections

    def toDict(self):
        return {
            "early_score": self.early_score,
            "late_score": self.late_score,
            "break_score": self.break_score,
            "reserved_score": self.reserved_score,
            "total_score": self.total_score}


class Evaluator:
    def __init__(self, preference, max_size):
        self.schedules = []
        self.max_size = max_size
        self.count = 0

        self.early_time = str_time2timedelta(preference["early_time"])
        self.late_time = str_time2timedelta(preference["late_time"])
        self.break_time = str_time2timedelta(preference["break_time"])
        self.early_weight = preference["early_weight"]
        self.late_weight = preference["late_weight"]
        self.break_weight = preference["break_weight"]

        def parse_reserved(slot): return TimeSlot(slot["from"], slot["to"],
                                                  slot["wiggle"], slot["weight"])

        self.reserved_slots = list(map(parse_reserved, preference["reserved"]))

    def __call__(self, sections):

        def early_evaluator(time):
            if time >= self.early_time:
                return 0
            else:
                return (self.early_time - time).total_seconds() * self.early_weight / 2000

        def late_evaluator(time):
            if time <= self.late_time:
                return 0
            else:
                return (time - self.late_time).total_seconds() * self.late_weight / 2000

        def break_evaluator(time):
            if time <= self.break_time:
                return 0
            else:
                return (time - self.break_time).total_seconds() * self.break_weight / 2000

        reserved_slots = self.reserved_slots

        timetable = Timetable()

        for section in sections:
            if section.exempt or not section.start or not section.end:
                continue
            for day in section.days:
                timetable.insert(day, section.start, section.end)

        early_score = 0
        late_score = 0
        break_score = 0
        reserved_score = 0

        # loop through days
        for day in timetable.timetable:

            # only calculate cost when there are sections on a day
            if len(day) == 0:
                continue

            start = day[0][0]
            end = day[-1][1]

            early_score += early_evaluator(start)
            late_score += late_evaluator(end)

            reserved_slots_copy = [slot for slot in reserved_slots
                                   if not (slot.fits_in(timedelta(0), start)
                                           or slot.fits_in(end, timedelta(days=1)))]

            # loop through breaks of that day
            for index in range(len(day) - 1):
                break_start = day[index][1]
                break_end = day[index + 1][0]
                break_len = break_end - break_start

                original_len = len(reserved_slots_copy)

                reserved_slots_copy = [slot for slot in reserved_slots_copy
                                       if not slot.fits_in(break_start, break_end)]

                # if the break does not satisfy any reserved slots
                if len(reserved_slots_copy) == original_len:
                    break_score += break_evaluator(break_len)

            for slot in reserved_slots_copy:
                reserved_score += slot.weight

        schedule = ResultSchedule([section.id for section in sections],
                                  early_score, late_score, break_score, reserved_score)

        if len(self.schedules) < self.max_size:
            heapq.heappush(self.schedules, schedule)
        elif self.schedules[0] < schedule:
            heapq.heappushpop(self.schedules, schedule)

        self.count += 1

    def get_results(self):
        result = []
        while len(self.schedules):
            result.append(heapq.heappop(self.schedules))
        result.reverse()
        return result


def part_list_from_coursebin(coursebin):
    groups = OrderedDict()

    def create_filter(parent=None):
        if parent is None:
            return lambda node: node.get("type") == "course" and not node.get("exclude")
        return lambda node: node.get("parent") == parent and not node.get("exclude")

    # for all courses
    for course in filter(create_filter(), coursebin):

        part_list = []
        # for all parts
        for part in filter(create_filter(course["node_id"]), coursebin):

            component_list = []
            # for all components
            for component in filter(create_filter(part["node_id"]), coursebin):
                section_list = [Section(node) for node in coursebin
                                if create_filter(component["node_id"])(node)]
                component_list.append(section_list)
            part_list.append(component_list)

        # group course parts according to course.group
        if course["group"] not in groups:
            groups[course["group"]] = []

        groups[course["group"]] += part_list

    return groups.values()


def part_combo_to_component_list(part_combinations):
    component_list = []
    for part in part_combinations:
        component_list += part
    return component_list


def dfs_search(components, index, selected, timetable, evaluator, terminate_at):

    if terminate_at and datetime.now() > terminate_at:
        raise TimeoutException()
    if not components:
        return

    if index >= len(components):
        evaluator(selected)
        return

    for section in components[index]:

        if section.exclude:
            continue

        timetable_copy = timetable.clone()
        is_valid = True
        if section.start and section.end:
            for day in section.days:
                if not timetable_copy.insert(day, section.start, section.end):
                    is_valid = False
                    continue

        if is_valid:
            selected.append(section)
            dfs_search(components, index+1, selected,
                       timetable_copy, evaluator, terminate_at)
            selected.pop()
