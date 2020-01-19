from collections import OrderedDict
import itertools
import bisect
import heapq
from datetime import datetime, time, timedelta
from .models import Schedule


def parse_time(str, pattern):
    return datetime.combine(datetime.min, datetime.strptime(str, pattern).time()) - datetime.min


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


class Evaluator:
    def __init__(self, preference, max_size):
        self.schedules = []
        self.max_size = max_size
        self.preference = preference
        self.count = 0

    def __call__(self, sections):

        if [29998, 30239, 30028, 31395, 30997, 31007, 31833, 31834, 29959, 30361, 30222, 25800, 25802, ] == [section["section_id"] for section in sections]:
            print('xxx')

        early_time = parse_time(
            self.preference["early_time"], "%H:%M")
        late_time = parse_time(
            self.preference["late_time"], "%H:%M")
        break_time = parse_time(
            self.preference["break_time"], "%H:%M")
        early_weight = self.preference["early_weight"]
        late_weight = self.preference["late_weight"]
        break_weight = self.preference["break_weight"]

        def early_evaluator(time):
            if time >= early_time:
                return 0
            else:
                return (early_time - time).total_seconds() * early_weight / 2000

        def late_evaluator(time):
            if time <= late_time:
                return 0
            else:
                return (time - late_time).total_seconds() * late_weight / 2000

        def break_evaluator(time):
            if time <= break_time:
                return 0
            else:
                return (time - break_time).total_seconds() * break_weight / 2000

        reserved_slots = []

        for slot in self.preference["reserved"]:
            reserved_slots.append((parse_time(slot["time"], "%H:%M"),
                                   parse_time(slot["length"], "%H:%M"),
                                   slot["weight"]))

        timetable = Timetable()

        for section in sections:
            if section.get("exempt") or not section.get("start") or not section.get("end"):
                continue
            for day in section["days"]:
                timetable.insert(day, parse_time(section["start"], "%H:%M:%S"),
                                 parse_time(section["end"], "%H:%M:%S"))

        early_score = 0
        late_score = 0
        break_score = 0
        reserved_score = 0

        for day in timetable.timetable:

            # only calculate cost when there are sections on a day
            if len(day) == 0:
                continue

            start = day[0][0]
            end = day[-1][1]

            early_score += early_evaluator(start)
            late_score += late_evaluator(end)

            reserved_slots_copy = list(filter(lambda slot: not (
                slot[0] <= start or slot[0] >= end), reserved_slots))

            for index in range(len(day) - 1):
                break_start = day[index][1]
                break_end = day[index + 1][0]

                is_reserved = False

                for slot in reserved_slots_copy:
                    if break_start <= slot[0] and slot[0] <= break_end\
                            and break_end - break_start >= slot[1]:
                        is_reserved = True
                        reserved_slots_copy.remove(slot)
                        break

                if not is_reserved:
                    break_score += break_evaluator(break_end - break_start)

            for slot in reserved_slots_copy:
                reserved_score += slot[2]

        schedule = ResultSchedule([section["id"] for section in sections],
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

    # for all courses
    for course in filter(lambda node: node.get("type") == "course", coursebin):

        part_list = []
        # for all parts
        for part in filter(lambda node: node.get("parent") == course["node_id"], coursebin):

            component_list = []
            # for all components
            for component in filter(lambda node: node.get("parent") == part["node_id"], coursebin):
                section_list = [node
                                for node in coursebin
                                if node.get("parent") == component["node_id"]]
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


def dfs_search(components, index, selected, timetable, evaluator):

    if not components:
        return

    if index >= len(components):
        evaluator(selected)
        return

    for section in components[index]:

        if section.get("exclude"):
            continue

        timetable_copy = timetable.clone()
        is_valid = True
        if section["start"] and section["end"]:
            for day in section["days"]:
                if not timetable_copy.insert(day, parse_time(section["start"], "%H:%M:%S"),
                                             parse_time(section["end"], "%H:%M:%S")):
                    is_valid = False
                    continue

        if is_valid:
            selected.append(section)
            dfs_search(components, index+1, selected, timetable_copy, evaluator)
            selected.pop()


def generate_schedule(coursebin, preference, task_instance):

    part_combinations = itertools.product(*part_list_from_coursebin(coursebin))

    evaluator = Evaluator(preference, 20)

    for combination in part_combinations:
        component_list = part_combo_to_component_list(combination)
        dfs_search(component_list, 0, list(), Timetable(), evaluator)

    results = evaluator.get_results()
    for result in results:
        schedule_instance = Schedule(task=task_instance,
                                     early_score=result.early_score,
                                     late_score=result.late_score,
                                     break_score=result.break_score,
                                     reserved_score=result.reserved_score,
                                     total_score=result.total_score,
                                     public=not task_instance.user)
        schedule_instance.save()
        schedule_instance.sections.add(*result.sections)
