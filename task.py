import datetime
import json
import sys


class Flight(object):
    """For easy retrival of attributes."""

    def __init__(self, row):
        (self.source,
         self.destination,
         self.departure,
         self.arrival,
         self.flight_number,
         self.price,
         self.bags_allowed,
         self.bag_price) = row


class FlightCombinator(object):
    """For avoidance of global variables."""

    def __init__(self, data, bags=0):
        self.bags = bags
        self._data = self.process_data(data)

    def convert_to_python(self, row):
        """We don't want to care about pythonizing strings."""
        (source,
         destination,
         departure,
         arrival,
         flight_number,
         price,
         bags_allowed,
         bag_price) = row
        return (source,
                destination,
                self.time_from_string(departure),
                self.time_from_string(arrival),
                flight_number,
                int(price),
                int(bags_allowed),
                int(bag_price))

    def flatten(self, list_of_lists):
        """Outcome of a recursive function has to be parsed."""
        big_list = []

        for item in list_of_lists:
            if isinstance(item[0], Flight):
                big_list.append(item)
            else:
                big_list.extend(self.flatten(item))

        return big_list

    def possibility(self, history):
        """Recursively find all possibilities given constraints."""
        current_flight = history[-1]
        visited_places = [flight.arrival for flight in history]

        possibilities = list(filter(
            lambda flight: (
                flight.source == current_flight.destination
                and flight.arrival not in visited_places
                and (flight.departure - current_flight.arrival).days == 0
                and (flight.departure - current_flight.arrival).seconds > 3600
                and (flight.departure - current_flight.arrival).seconds < 3600 * 4
                and flight.bags_allowed >= self.bags
            ),
            self.data))

        if not possibilities:
            return history if (len(history) > 1) else None

        return [self.possibility(history + [option]) for option in possibilities]

    def pretty_print(self, combination):
        """One of inf ways to print the results. Suitable for reading?"""
        start = combination[0].source
        end = [flight.destination for flight in combination]
        return (
            "->".join([start] + end),
            [flight.flight_number for flight in combination],
            sum(flight.price for flight in combination)
        )

    def process_data(self, data):
        """Create "Flight" instanes from raw data."""
        return [Flight(self.convert_to_python(row)) for row in data]

    def return_all(self, bags=0):
        """Main entry point."""
        self.update_bags(bags)
        all_possibilities = list(filter(
            lambda x: x,
            [self.possibility([flight]) for flight in self.data]
        ))

        return [self.pretty_print(flight) for flight in self.flatten(all_possibilities)]

    @staticmethod
    def time_from_string(time_string):
        return datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S")

    def update_bags(self, bags):
        """Constrain current self.data given bag concerns."""
        self.bags = bags
        self.data = [flight for flight in self._data if flight.bags_allowed >= self.bags]


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
