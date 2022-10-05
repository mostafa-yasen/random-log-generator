#!/usr/bin/env python3

import argparse
import os
import traceback
from collections import Counter, defaultdict
from datetime import datetime

import humanize

from models import Record


class Solution:
  def __init__(self, filepath: str) -> None:
    self.filepath = filepath

  def run(self):
    try:
      self.main()
    except Exception:
      traceback.print_exc()

  def main(self):
    with open(self.filepath, "r") as f:
      records = f.read().split("\n")
      self.records = list(map(Record.from_str, records))

    self.print_allowed_source_ips()
    
    self.print_top_denied_users()

    self.print_bypass_services_percent()

    self.print_rush_hours()

  def print_allowed_source_ips(self):
    """Top 10 Allowed source IPs"""
    occurence_count = Counter(self.records)
    print("Top 10 Allowed source IPs")
    # for i in range(10):
    ips = list(map(lambda x: str(x[0].user.get_ip()), occurence_count.most_common(10)))
    for index, ip in enumerate(ips):
      print(f"{index + 1} - {ip}")

  def print_top_denied_users(self):
    """10 Denied users and Top 5 destination IPs for each user"""
    print()
    groups = defaultdict(list)
    for record in self.records:
      groups[record.action].append(record)

    occurence_count = Counter(groups["Deny"])
    print("Top 10 Denied Users")
    records = list(map(lambda x: str(x[0].user.username), occurence_count.most_common(10)))
    for i, record in enumerate(records):
      print(f"{i} - {record}")
    # TODO: Print top 5 destination IPs for each user.

  def print_bypass_services_percent(self):
    """Percentage of Bypassed TCP services and The Top 5 services"""
    print()
    groups = defaultdict(list)
    for record in self.records:
      if record.action != "Bypass":
        continue

      groups[record.port.protocol].append(record)

    tcp_logs = groups["TCP"]
    try: 
      percent = (len(tcp_logs) * 100 / len(self.records))
      percent = "%.2f" % percent
      # percent = humanize.fractional(percent)
      print(f"Percentage of Bypassed TCP services: {percent}%")

    except ZeroDivisionError:
      print("Something went wrong, it seems like the file is empty.")
    # TODO: It's not clear to me. What are Top 5 services?

  def print_rush_hours(self):
    """Top 5 hours within the log file duration in terms of unique users count"""
    print()
    records = sorted(self.records, key=lambda x: x.datetime.time())
    groups = defaultdict(list)
    for record in records:
      groups[record.datetime.time()].append(record)

    print("Top 5 hours within the log file duration")
    output = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)
    for i in range(5):
      time, records = output[i]
      print(f"time: {time}, requests: {len(records)}")


if __name__ == "__main__":
  start = datetime.now()
  parser = argparse.ArgumentParser(description="Analyses a given log file.")
  parser.add_argument(
    "-f", "--file", type=str, nargs=1, metavar="file",
    default=None, help="File to be analysed.", required=True)

  args = parser.parse_args()
  file = "output.log"
  if args.file:
    file = args.file[0]

  Solution(filepath=file).run()

  file_stat = os.stat(file)
  file_size = humanize.naturalsize(file_stat.st_size)
  print()
  print(f"Log file size: {file_size}")

  duration = datetime.now() - start
  duration = humanize.precisedelta(duration)
  print(f"Process done in {duration}.")
