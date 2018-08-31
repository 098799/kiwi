import json
import datetime
import sys


class FlightCombinator(object):
    def __init__(self, data, bags=0):
        self.bags = bags
        self._data = self.process_data(data)

    def convert_date(self, row):
        arrival, departure, time_departure, time_arrival, *rest = row
        return (arrival,
                departure,
                self.time_from_string(time_departure),
                self.time_from_string(time_arrival),
                *rest)

    def flatten(self, list_of_lists):
        big_list = []

        for item in list_of_lists:
            if isinstance(item[0], tuple):
                big_list.append(item)
            else:
                big_list.extend(self.flatten(item))

        return big_list

    @staticmethod
    def get_allowed_bags(row):
        return int(row[6]) if row else 2

    @staticmethod
    def get_flight_number(row):
        return row[4]

    @staticmethod
    def get_place(row, which):
        if which == "departure":
            return row[0] if row else None
        elif which == "arrival":
            return row[1] if row else None

    @staticmethod
    def get_price(row):
        return int(row[5])

    @staticmethod
    def get_time(row, which):
        if which == "departure":
            return row[2] if row else None
        elif which == "arrival":
            return row[3] if row else None

    def possibility(self, history):
        current_row = history[-1]
        current_place = self.get_place(current_row, "arrival")
        current_time = self.get_time(current_row, "arrival")
        visited_places = [self.get_place(row, "arrival") for row in history]

        possibilities = list(filter(
            lambda row: (
                self.get_place(row, "departure") == current_place
                and self.get_place(row, "arrival") not in visited_places
                and (self.get_time(row, "departure") - current_time).days == 0
                and (self.get_time(row, "departure") - current_time).seconds > 3600
                and (self.get_time(row, "departure") - current_time).seconds < 3600 * 4
                and (self.get_allowed_bags(row) >= self.bags)
            ),
            self.data))

        if not possibilities:
            return history if (len(history) > 1) else None

        return [self.possibility(history + [option]) for option in possibilities]

    def pretty_print(self, combination):
        start = self.get_place(combination[0], "departure")
        end = [self.get_place(row, "arrival") for row in combination]
        return (
            "->".join([start] + end),
            [self.get_flight_number(row) for row in combination],
            sum(self.get_price(row) for row in combination)
        )

    def process_data(self, data):
        return [self.convert_date(row) for row in data]

    def return_all(self, bags=0):
        self.update_bags(bags)
        all_possibilities = list(filter(lambda x: x,
                                        [self.possibility([row])
                                         for row in self.data]))

        return [self.pretty_print(row) for row in self.flatten(all_possibilities)]

    @staticmethod
    def time_from_string(time_string):
        return datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S")

    def update_bags(self, bags):
        self.bags = bags
        self.data = [row for row in self._data if self.get_allowed_bags(row) >= self.bags]


def import_data():
    data = []
    for line in sys.stdin:
        data.append(line.rstrip("\n").split(","))
    return data[1:]


def main():
    try:
        data = import_data()
    except Exception as e:
        print("Input reading failed with exception {}".format(e), file=sys.stderr)
        return

    try:
        flight_combinator = FlightCombinator(data)
    except Exception as e:
        print("Class initialization failed with exception {}".format(e), file=sys.stderr)
        return

    output = {}

    for bags in range(3):
        try:
            output[bags] = flight_combinator.return_all(bags=bags)
        except Exception as e:
            print("The following exception happened: {}".format(e), file=sys.stderr)
            return

    print(json.dumps(output))


if __name__ == "__main__":
    main()
