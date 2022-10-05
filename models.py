import re
from datetime import datetime, time
from random import randint


class Port:
  def __init__(self, number: int, protocol: str) -> None:
    self.number = number
    self.protocol = protocol


class User(object):
  def __init__(self, username: str, ip_addresses: list) -> None:
    if not re.match("^[a-zA-Z_.]+$", username):
      raise Exception("Username is any alphanumeric word that doesn't start with a digit")

    if len(ip_addresses) not in [1, 2]:
      raise Exception("Each user cannot have more than 2 distinct source IPs")

    self.username = username
    self.ip_addresses = ip_addresses

  def get_ip(self) -> str:
    if len(self.ip_addresses) > 1:
      return self.ip_addresses[randint(0, 1)]
    return self.ip_addresses[0]


class Condiotions:
  def __init__(
      self, allow_limit: float, deny_limit: float,
      bypass_min: float, user_ip_count_limit: int,
      start_date: datetime, end_date: datetime,
      rush_hours_start: time, rush_hours_end: time,
      rush_hours_threshold: float) -> None:

    self.allow_limit = allow_limit
    self.deny_limit = deny_limit
    self.bypass_min = bypass_min
    self.user_ip_count_limit = user_ip_count_limit
    self.start_date = start_date
    self.end_date = end_date
    self.rush_hours_start = rush_hours_start
    self.rush_hours_end = rush_hours_end
    self.rush_hours_threshold = rush_hours_threshold


class Record(object):
  def __init__(
      self, datetime: datetime, port: Port,
      user: User, dest:str, action: str) -> None:
    self.datetime = datetime
    self.port = port
    self.user = user
    self.dest = dest
    self.action = action

  def __str__(self):
    template = "{date} {time} {source_ip} {dest} {port} {protocol} {username} {action}"
    return template.format(
      date=self.datetime.date(),
      time=self.datetime.time(),
      source_ip=self.user.get_ip(),
      dest=self.dest,
      port=self.port.number,
      protocol=self.port.protocol,
      username=self.user.username,
      action=self.action
    )
