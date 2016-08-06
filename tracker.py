import os
import sys
import time

import psutil

import re

import requests

import xml.etree.ElementTree as etree

'''
  mode -1 = Unknown, will exit
  mode  0 = Wait until Audiosurf2 exits, then read file as a whole
  mode  1 = Watch file and read as it's updated
'''
mode = -1

last_modified_time = 0

curr_xml = ""
append = False

song_name = ""
song_artist = ""
song_duration = 0
score = 0

score_pattern = re.compile("^\$#\$ setting score (\d+) for song: .+")
song_pattern = re.compile("^sending score\. title:(.+) duration:(\d+) artist:(.+)$")

def find_as2_log():
  global mode
  if sys.platform == "linux":
    mode = 1
    return os.getenv("HOME") + "/.config/unity3d/Audiosurf, LLC/Audiosurf 2/Player.log"

def is_as2_running():
  try:
    process_names = [psutil.Process(i).name() for i in psutil.pids()]
  except psutil.NoSuchProcess:
    return False
  if ("Audiosurf2.x86" in process_names
    or "Audiosurf2.x86_64" in process_names):
    return True
  return False

def append_xml(sbs_tag, tag, sbs, name):
  sb = etree.SubElement(sbs_tag, tag)
  entries = etree.SubElement(sb, "Entries")
  for e in sbs.find('scoreboard[@name=\'' + name + '\']'):
    entry = etree.SubElement(entries, "Entry")
    etree.SubElement(entry, "UserID").text = e.get("userid")
    etree.SubElement(entry, "SteamID").text = e.get("steamid")
    etree.SubElement(entry, "Score").text = e.get("score")
    etree.SubElement(entry, "RideTime").text = e.get("ridetime")
    etree.SubElement(entry, "Mode").text = e.find("modename").text
    etree.SubElement(entry, "Comment").text = e.find("comment").text if e.find("comment") is not None else " "
    etree.SubElement(entry, "Username").text = e.find("username").text

def handle_xml(title, artist, duration, score, xml):
  # Parse Audiosurf XML to our format
  root = etree.fromstring(xml)
  user = root.find('user')
  modename = root.find('modename')
  scoreboards = root.find('scoreboards')
  song_id = scoreboards.get("songid")

  sroot = etree.Element("ArrayOfSong")
  ssong = etree.SubElement(sroot, "Song")
  sscores = etree.SubElement(ssong, "Scores")
  sscore = etree.SubElement(sscores, "Score")
  etree.SubElement(sscore, "Mode").text = modename.get("modename")
  etree.SubElement(sscore, "Value").text = score
  sscoreboard = etree.SubElement(ssong, "Scoreboard")
  append_xml(sscoreboard, "Global", scoreboards, "public")
  append_xml(sscoreboard, "Friends", scoreboards, "friends")
  append_xml(sscoreboard, "Regional", scoreboards, "region")
  etree.SubElement(ssong, "Title").text = title
  etree.SubElement(ssong, "Artist").text = artist
  etree.SubElement(ssong, "Duration").text = duration
  etree.SubElement(ssong, "SongID").text = song_id
  etree.SubElement(ssong, "UserID").text = user.get("userid")
  etree.SubElement(ssong, "UserRegion").text = user.get("regionid")
  etree.SubElement(ssong, "UserEmail").text = user.get("email")
  etree.SubElement(ssong, "CanPostScore").text = user.get("canpostscores")

  # Send XML to server
  xml_string = etree.tostring(sroot, encoding="utf-8")
  print(xml_string)
  r = requests.post("http://www.as2tracker.com/input_new.php", data={
    "xml": xml_string
  })
  if r.status_code == 200:
    print("Sent score for", title, "-", artist, "http://as2tracker.com/song/" + song_id)
  else:
    print("Failed to send score, error", r.status_code)
    print(r.text)

def handle_line(line):
  global song_pattern, song_name, song_duration, song_artist, score_pattern, score, curr_xml, append
  sline = line.strip()
  if song_pattern.match(sline):
    m = song_pattern.search(sline)
    song_name = m.group(1)
    song_duration = m.group(2)
    song_artist = m.group(3)
  elif score_pattern.match(sline):
    m = score_pattern.search(sline)
    score = m.group(1)
  elif sline.startswith("<?xml"):
    curr_xml = line
    append = True
  elif sline.endswith("</document>"):
    curr_xml += line
    append = False
    handle_xml(song_name, song_artist, song_duration, score, curr_xml)
  elif append:
    curr_xml += line

def main():
  global last_modified_time

  log_path = find_as2_log()

  if mode == -1:
    print("Unknown OS:", sys.platform)
    sys.exit(1)
  elif mode == 0:
    while (is_as2_running()):
      time.sleep(2)
    curr_modified_time = os.stat(log_path).st_mtime
    if (last_modified_time < curr_modified_time):
      last_modified_time = curr_modified_time
      with open(log_path, 'r', encoding="ISO-8859-1") as f:
        for line in f.readlines():
          handle_line(line)
  elif mode == 1:
    with open(log_path, 'r', encoding="ISO-8859-1") as f:
      prev_size = 0
      curr_size = os.stat(log_path).st_size
      
      f.seek(curr_size)

      while 1:
        curr_size = os.stat(log_path).st_size
        if (prev_size > curr_size):
          break
        prev_size = curr_size
        where = f.tell()
        line = f.readline()
        if not line:
          time.sleep(1)
          f.seek(where)
        else:
          handle_line(line)

if __name__ == "__main__":
  while 1:
    main()
    time.sleep(2)
