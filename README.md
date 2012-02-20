mediatools
==========

syncitunes.py
-------------

Sync your iTunes library from a script.  This script has two commands "--prune" and "--scan=$path".  "--prune" removes tracks that no longer have a path.   I invoke this like "python syncitunes.py --prune --scan=/Volumes/KnockKnock/media".  There's a verbose mode ("--verbose") if you want to see that it's doing work.  Interacting with iTunes is relatively slow.  On my 1.6ghz Mac Mini traversing the list of 24K tracks takes around 6 minutes.  "--scan=$path"  scans a path.  It can be specified multiple times.   I run this from a cron to keep my library automatically update to date.
