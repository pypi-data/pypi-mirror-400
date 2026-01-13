class Weekday:
    def __init__(self, id, name):
        self.id = id
        self.name = name

MONDAY = Weekday(0, "Monday")
TUESDAY = Weekday(1, "Tuesday")
WEDNESDAY = Weekday(2, "Wednesday")
THURSDAY = Weekday(3, "Thursday")
FRIDAY = Weekday(4, "Friday")
SATURDAY = Weekday(5, "Saturday")
SUNDAY = Weekday(6, "Sunday")
WEEKDAYS = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY]