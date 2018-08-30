import csv
import datetime


def time_from_row(row, which):
    if which == "departure":
        return time_from_string(row[2])
    elif which == "arrival":
        return time_from_string(row[3])


def time_from_string(time_string):
    return datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S")


def time_interval_in_hours(time1, time2):
    return (time1 - time2).seconds/3600


def possibility(data, place, time):  # , bags):
    current_time = time_from_string(time)

    return list(filter(
        lambda x: (
            x[0] == place
            and time_interval_in_hours(current_time, time_from_row(x, "departure")) > 1
            and time_interval_in_hours(current_time, time_from_row(x, "departure")) < 4
        ),
        data)
    )


with open("data.csv", newline="") as infile:
    read_object = csv.reader(infile, delimiter=",")

    headers = next(read_object)
    data = []

    for row in read_object:
        data.append(row)

print(possibility(data, "USM", "2017-02-11T06:15:00"))
