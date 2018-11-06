# 10 minute mail domains list

A Python script (and weekly update list), which grabbing domains from sites provides shortlife email address.

### Why?

My last two jobs required this list with updates (at least once per month). Do not want to think about it anymore, just code it. 150 LOCs, simple logic.

### Is there something similar?

Yes, but its either paid or old:
- we arent interest in outdated
- all payable API created with low limits like 1000 requests per day for 50$

### How do you make updates?
``echo -e 'MAILTO=myemail@mydomain.com\n0 0 * * * cd ~/src/AlexDyukov/10minutemail_list/; python3 10minutemail_grabber.py | sort > latest.list; git commit -am "update $(date)" --quiet && git push --quiet' > /etc/cron.d/10minutemail``.

### Why did you make hardcoded variables?

Main things of this project: the list, not the script. Hardcoded variables would be as long as there is no need for it.

