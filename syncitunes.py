import logging
import optparse
import os
import re
import struct
import urlparse
import urllib
from Foundation import *
from ScriptingBridge import *
 
itunes = SBApplication.applicationWithBundleIdentifier_("com.apple.iTunes")

lib = itunes.sources()[0].playlists()[0]
_media_pat = re.compile('^.*(mp3|mkv|avi|m4a|ogg|aac|mp4)$', re.I)

log = logging.getLogger('syncitunes')
opts = None
args = None

def get_tracks():
  for t in lib.tracks():
    f = t.get()
    if f is not None:
      yield f

def prune():
  for t in get_tracks():
    try:
      l = t.location()
    except AttributeError:
      continue
    if not l:
      continue
    if not l.isFileURL():
      continue
    file_mgr = NSFileManager.defaultManager()
    if not file_mgr.fileExistsAtPath_(l.path()):
      logging.debug('removing %r', l)
      t.remove()

def scan_directory(path):
  file_mgr = NSFileManager.defaultManager()
  if not isinstance(path, unicode):
    path = path.decode('utf-8')
  exists, is_dir = file_mgr.fileExistsAtPath_isDirectory_(path, None)
  if not exists:
    log.info('%r exists', path)
    return
  if not is_dir:
    log.info('%r is not a directory', path)
    return

  existing_paths = set()
  for t in get_tracks():
    try:
      l = t.location()
    except AttributeError:
      pass
    if not l:
      continue
    if not l.isFileURL():
      continue
    existing_paths.add(l.path())

  for directory, _, filenames in os.walk(path.encode('utf-8')):
    for filename in filenames:
      p = '%s/%s' % (directory, filename)
      p = p.decode('utf-8') 

      if not _media_pat.match(p):
        continue

      if p not in existing_paths:
        url = NSURL.fileURLWithPath_(p)
        itunes.add_to_([url], None)

def scan_directory2(path):
  file_mgr = NSFileManager.defaultManager()
  if not isinstance(path, unicode):
    path = path.decode('utf-8')
  exists, is_dir = file_mgr.fileExistsAtPath_isDirectory_(path, None)
  if not exists:
    print path, "exists"
    return
  if not is_dir:
    print path, "is not a directory"
    return
  url = NSURL.fileURLWithPath_(path)
  itunes.add_to_([url], None)

def walk_media(path):
  file_mgr = NSFileManager.defaultManager()
  if not isinstance(path, unicode):
    path = path.decode('utf-8')
  exists, is_dir = file_mgr.fileExistsAtPath_isDirectory_(path, None)
  if not exists:
    log.error("exists: %r", path)
    return
  if not is_dir:
    log.error("is not a directory: %r", path)
    return

  log.info('loading existing paths')
  existing_paths = set()
  for t in get_tracks():
    try:
      l = t.location()
    except AttributeError:
      pass
    if not l:
      continue
    if not l.isFileURL():
      continue
    existing_paths.add(l.path())
  log.debug('%d existing paths', len(existing_paths))

  for directory, _, filenames in os.walk(path.encode('utf-8')):
    for filename in filenames:
      p = '%s/%s' % (directory, filename)
      p = p.decode('utf-8') 

      if not _media_pat.match(p):
        continue

      if p not in existing_paths:
        url = NSURL.fileURLWithPath_(p)
        yield url

def chunks(items, n): 
  chunk = []
  for item in items:
    if len(chunk) >= n:
      yield chunk
      chunk = []
    chunk.append(item)
  if chunk:
    yield chunk

def scan_directory3(path):
  log.info('scanning %s', path) 
  for chunk in chunks(walk_media(path), opts.chunk):
    log.debug('adding chunk (%d)', len(chunk))
    itunes.add_to_(chunk, None)
    log.debug('done')

def main():
  global opts
  global args

  parser = optparse.OptionParser()
  parser.add_option('--prune', default=False, action='store_true')
  parser.add_option('--scan', action='append')
  parser.add_option('--chunk', type='int', default=100, help='add this many files at once')
  parser.add_option('--verbose', default=[], action='store_true')

  opts, args = parser.parse_args()

  logging.basicConfig(level=logging.DEBUG if opts.verbose else logging.INFO, 
    format="%(asctime)s %(levelname)s %(name)s %(message)s")

  if opts.prune:
    prune()
  for a in opts.scan:
    scan_directory3(a)

if __name__ == '__main__':
  main()

