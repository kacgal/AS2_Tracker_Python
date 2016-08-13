## AS2 Tracker
#### Python 3 version of https://github.com/bayrock/AS2_Tracker/

Upload scores from [Audiosurf2](http://store.steampowered.com/app/235800/) to [AS2Tracker](http://as2tracker.com)

Features:
- Multiplatform! Linux / Windows / Mac are all supported
- Announce current song in your [Twitch.TV](https://twitch.tv) chat
- Scans the log file as you play
 
Note: The current song announcer doesn't work with the bleedingedge beta

Installation:  
0. Make sure you have [Python3](https://www.python.org/downloads/) installed (`python -V` to check)  
1. Clone this repo (Or just download the [tracker.py](https://raw.githubusercontent.com/kacgal/AS2_Tracker_Python/master/tracker.py) file)  
2. Install dependencies with `pip install -r requirements.txt`  
3. Run `python tracker.py --twitch-username <username> --twitch-oauth-key <oauth key>`  

Arguments:
- --debug : Enable debug mode
- --read-whole-file : Scan the whole log file for scores
- --twitch-username <username> : Your twitch username
- --twitch-oauth-key <oauth key> : Your OAuth key (can be gotten from [here](http://www.twitchapps.com/tmi/))
- --twitch-message-format <format> : Message format, sent when starting song, variables: {title} and {artist}
- --twitch-result-format <format> : Result format, sent when  song finished, {title}, {artist}, {score}, {position} and {position_suffix}

### Testing has been very limited, it's very possible this might not work on your machine
### Bug reports are always welcome
