#!/usr/bin/env python3

import argparse
import traceback
from datetime import datetime, time, timedelta
from math import floor
from random import randint

from names import get_full_name
from tqdm import tqdm

from models import *
import humanize

# from functools import lru_cache


class Solution(object):
  def __init__(self) -> None:
    self.users = list(self.generate_users())
    self.ports = self.generate_ports()

  def generate_users(self):
    """Generates a random 500 users that conform to the condition. 
    'Only 500 unique users and 650 unique source IPs are allowed'
    """
    for i in tqdm(range(500), desc="Generating 500 users", ncols=100):
      ip_addresses = [self.get_random_ip()]
      if i <= 150: ip_addresses.append(self.get_random_ip())
      yield User(self.get_random_username(), ip_addresses)

  def generate_ports(self):
    return [
      Port(20, "TCP"),
      Port(21, "TCP"),
      Port(22, "UDP"),
      Port(23, "TCP"),
      Port(25, "TCP"),
      Port(53, "UDP"),
      Port(80, "TCP"),
      Port(194, "UDP"),
      Port(443, "TCP")
    ]

  def run(self, *args, **kwargs) -> None:
    try:
      self.main(*args, **kwargs)
    except Exception as e:
      traceback.print_exc()

  def main(self, *args, **kwargs) -> None:
    records = []
    lines_count = kwargs.get("lines_count", 100)
    conditions = Condiotions(
      # Less than 50% of the entries should be Allow
      allow_limit=0.5,
      
      # Less than 10% of the traffic should be Deny
      deny_limit=0.1,
      
      # At least 15% of the entries should be Bypass
      bypass_min=0.15,

      # Each user cannot have more than 2 distinct source IPs
      user_ip_count_limit=2,

      # The log covers the duration between 2019-10-20 01:00 and 2019-10-30 18:00
      start_date=datetime(2019, 10, 20, 1, 0, 0, 0),
      end_date=datetime(2019, 10, 30, 18, 0, 0, 0),

      # 70% of the requests happen during the day (between 09:00-18:00)
      rush_hours_start=time(9, 0, 0, 0),
      rush_hours_end=time(18, 0, 0, 0),
      rush_hours_threshold=0.7
    )

    dates_delta = (conditions.end_date - conditions.start_date).days
    lines_per_day = lines_count /  dates_delta
    for day in tqdm(range(dates_delta), desc="Generating Logs", ncols=100):
      date = conditions.start_date + timedelta(days=day)
      date_records = []
      while len(date_records) < lines_per_day:
        t = time(
          [randint(0, 9), randint(19, 23)][randint(0, 1)],
          0, 0, 0
        )
        action = "Log-only"
        allow_action_count = floor(conditions.allow_limit * lines_per_day)
        deny_action_count = floor(conditions.deny_limit * lines_per_day)
        bypass_action_count = floor(conditions.bypass_min * lines_per_day)
        rush_hours_count = floor(conditions.rush_hours_threshold * lines_per_day)
        if len(date_records) < rush_hours_count:
          t.replace(hour=randint(
            conditions.rush_hours_start.hour,
            conditions.rush_hours_end.hour
          ))

        # (allow_action_count * 0.9) -> subs 10% from the limit to assure it's less than the limit.
        if len(date_records) < allow_action_count * 0.9:
          action = "Allow"

        # (deny_action_count * 0.8) -> subs 20% from the limit to assure it's less than the limit.
        elif len(date_records) < allow_action_count + (deny_action_count * 0.8):
          action = "Deny"

        # (bypass_action_count * 1.1) -> adds 10% to aussure it's more than the limit
        elif len(date_records) <= allow_action_count + deny_action_count + (bypass_action_count * 1.1):
          action = "Bypass"

        date_records.append(Record(
          date.replace(hour=t.hour),
          self.get_random_port(),
          self.get_random_user(),
          self.get_random_ip(),
          action
        ))

      records += date_records

    output_file = kwargs.get("output_file") or "output.log"
    with open(output_file, "w") as f:
      for i in tqdm(range(len(records)), desc=f"Writing {output_file}", ncols=100):
        f.write(str(records[i]) + "\n")

      # f.write("\n".join(map(str, records)))

    print(f"Records written into the file {output_file}")

  # @lru_cache(maxsize=10)
  def get_random_port(self) -> Port:
    return self.ports[randint(0, len(self.ports) - 1)]

  def get_random_ip(self) -> str:
    return ".".join([str(randint(0, 255)) for _ in range(4)])

  def get_random_username(self) -> str:
    gender = ["male", "female"][randint(0, 1)]
    return get_full_name(gender=gender).lower().replace(" ", "_")

  def get_random_user(self) -> User:
    return self.users[randint(0, len(self.users) - 1)]


if __name__ == "__main__":
  start = datetime.now()
  parser = argparse.ArgumentParser(description="A random logs file generator tool")
  parser.add_argument(
    "-o", "--output", type=str, nargs=1, metavar="output_file",
    default=None, help="File to write generated content into. "
      "Default is 'output.log'.")

  parser.add_argument(
    "-c", "--count", type=int, nargs=1, metavar="lines_count",
    default=100, help="Count of lines to be generated. Default is 100.")

  args = parser.parse_args()
  output_file = "output.log"
  if args.output:
    output_file = args.output[0]

  length = 100
  if args.count and type(args.count) is int:
    length = args.count
  elif args.count and type(args.count) is list:
    length = args.count[0]

  Solution().run(
    output_file=output_file,
    lines_count=length
  )
  execution_time = (datetime.now() - start)
  execution_time = humanize.precisedelta(execution_time)
  print(f"Process done in {execution_time}")
