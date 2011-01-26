#!/usr/bin/env python
# -*- coding: euc-jp -*-

import re, sys, time


##  RoffParser
##
class RoffParser(object):

  def feedfile(self, fp, encoding='ascii'):
    for line in fp:
      line = unicode(line.rstrip(), encoding, 'ignore')
      self.parse_line(line)
    return
  
  def close(self):
    return
  
  def parse_line(self, line):
    if line.startswith('.\\"'):
      # comment
      pass
    elif line.startswith('.'):
      i = 2
      self.cmd = line[1]
      self.args = []
      self.parse1 = self.parse_command
      line += ' '
      while i < len(line):
        (self.parse1, i) = self.parse1(line, i)
      self.do_command(self.cmd, self.args)
    else:
      i = 0
      self.parse1 = self.parse_main
      while i < len(line):
        (self.parse1, i) = self.parse1(line, i)
    return
  
  def parse_command(self, s, i):
    c = s[i]
    if c.isalpha():
      self.cmd += c
      return (self.parse_command, i+1)
    return (self.parse_arg0, i)
  
  def parse_arg0(self, s, i):
    c = s[i]
    if c.isspace():
      return (self.parse_arg0, i+1)
    self.arg1 = ''
    return (self.parse_arg1, i)
  
  def addarg(self, c):
    self.arg1 += c
    return
  
  def parse_arg1(self, s, i):
    c = s[i]
    if c == '\\':
      self.prev = self.parse_arg1
      self.addch = self.addarg
      return (self.parse_escape1, i+1)
    if c == '"':
      return (self.parse_arg_quote, i+1)
    if c.isspace():
      self.args.append(self.arg1)
      return (self.parse_arg0, i+1)
    self.arg1 += c
    return (self.parse_arg1, i+1)
  
  def parse_arg_quote(self, s, i):
    c = s[i]
    if c == '\\':
      self.prev = self.parse_arg_quote
      self.addch = self.addarg
      return (self.parse_escape1, i+1)
    if c == '"':
      self.args.append(self.arg1)
      return (self.parse_arg0, i+1)
    self.arg1 += c
    return (self.parse_arg_quote, i+1)
  
  def parse_main(self, s, i):
    e = s.find('\\', i)
    if e == -1:
      self.handle_text(s[i:])
      return (self.parse_main, len(s))
    self.prev = self.parse_main
    self.addch = self.handle_text
    return (self.parse_escape1, e+1)
  
  def parse_escape1(self, s, i):
    c = s[i]
    if c in '\\eE &-':
      self.addch(self.handle_escape(c, None))
      return (self.prev, i+1)
    self.ecmd = c
    return (self.parse_escape2, i+1)
  
  def parse_escape2(self, s, i):
    c = s[i]
    if c == '(':
      self.earg = '' # \a(XX
      return (self.parse_escape_arg2, i+1)
    if c == '[':
      self.earg = '' # \*[nnn]
      return (self.parse_escape_argn, i+1)
    self.earg = c
    self.addch(self.handle_escape(self.ecmd, self.earg))
    return (self.prev, i+1)
  
  def parse_escape_arg2(self, s, i):
    self.earg += s[i]
    if len(self.earg) == 2:
      self.addch(self.handle_escape(self.ecmd, self.earg))
      return (self.prev, i+1)
    return (self.parse_escape_arg2, i+1)
  
  def parse_escape_argn(self, s, i):
    if s[i] == ']':
      self.addch(self.handle_escape(self.ecmd, self.earg))
      return (self.prev, i+1)
    self.earg += s[i]
    return (self.parse_escape_argn, i+1)
    
  def do_command(self, cmd, args):
    f = 'do_command_'+cmd.replace('%','p_').lower()
    if hasattr(self, f):
      getattr(self, f)(args)
    else:
      self.do_unknown_command(cmd, args)
    return
  
  def handle_escape(self, cmd, arg):
    print >>sys.stderr, 'ESCAPE:', cmd, arg
    return
  
  def handle_text(self, s):
    print >>sys.stderr, 'TEXT:', s
    return
  
  def do_unknown_command(self, cmd, args):
    print >>sys.stderr, 'UNKNOWN:', cmd, args
    return


##  Roff2HTML
##
class Roff2HTML(RoffParser):

  HEADER = u'''<html>
<head>
<style><!--
.info { font-size: 80%; }
.op { left-margin: 4em; }
.name { font-weight: bold; }
.nm { font-weight: bold; }
.xr { }
.cite { font-style: italic; }
.arg { font-style: italic; text-decoration: underline; }
.flag { }
.env { }
.config { font-weight: bold; }
.file { font-weight: bold; }
.cmdline { background: #eee; margin: 0.5em; padding: 0.5em; }
--></style>
'''
  XREF = [
    'scp', 'sftp', 'sftp-server',
    'ssh-add', 'ssh-agent', 'ssh-keygen',
    'ssh-keyscan', 'ssh-rand-helper',
    'ssh', 'sshd', 'ssh_config', 'sshd_config',
    ]       
  
  def __init__(self, headline, fp=sys.stdout, encoding='ascii'):
    self.headline = headline
    self.fp = fp
    self.stack = []
    self.state = None
    self.name = None
    self.sm = False
    self.encoding = encoding
    self.write(self.HEADER)
    self.write('<meta http-equiv="Content-Type" content="text/html; charset=%s">' %
               encoding)
    return
  
  def write(self, s):
    self.fp.write(s.encode(self.encoding, 'ignore'))
    return

  def close(self):
    RoffParser.close(self)
    self.write('\n</body>\n</html>\n')
    return
    
  def handle_text(self, s):
    self.write(s)
    return

  def push(self, state):
    self.stack.append(self.state)
    self.state = state
    return
  
  def pop(self):
    self.state = self.stack.pop()
    return

  def handle_escape(self, cmd, arg):
    if cmd in '\\eE':
      return '\\'
    if cmd == ' ':
      return '&nbsp;'
    if cmd == '-':
      return '-'
    if cmd == '*':
      if arg == 'Lt':
        return '&lt;'
      elif arg == 'Gt':
        return '&gt;'
      return '[%s]' % arg
    return ''

  IS_CMD = re.compile(r'^[A-Z][a-z]$')
  def do_remain(self, args):
    while args:
      x = args.pop(0)
      if self.IS_CMD.match(x):
        return self.do_command(x, args)
      self.write(x)
    return
  
  def do_command_sh(self, args):
    s = ' '.join(args)
    self.write('<hr>\n<h2><a href="#%s" name="%s">%s</a></h2>\n' %
               (s,s,s))
    return
  
  def do_command_dt(self, args):
    (title, section) = args
    s = '%s (%s)' % (title, section)
    self.write('<title>%s</title>\n' % s)
    self.write('</head><body>\n')
    self.write('<h1>%s</h1>\n' % s)
    self.write('<p class=info>%s\n' % self.headline)
    return
  
  def do_command_nd(self, args):
    self.write('<blockquote>%s</blockquote>\n' % ' '.join(args))
    return
  
  def do_command_op(self, args):
    cmd = None
    self.write(' [')
    self.do_remain(args)
    self.write(']\n')
    return

  def do_command_oo(self, args):
    self.write(' [')
    self.do_remain(args)
    return
  
  def do_command_oc(self, args):
    self.write('] ')
    self.do_remain(args)
    return
  
  def do_command_ar(self, args):
    if args:
      self.write('<span class="arg">%s</span> ' % args.pop(0))
    else:
      self.write('<span class="arg">%s</span> ' % 'file')
    self.do_remain(args)
    return
  
  def do_command_fl(self, args):
    if args:
      self.write('<code><span class="flag">-%s</span></code> ' % args.pop(0))
    self.do_remain(args)
    return
  
  def do_command_ev(self, args):
    if args:
      self.write('<span class="env">%s</span> ' % args.pop(0))
    self.do_remain(args)
    return
  
  def do_command_sm(self, args):
    self.sm = (args[0].lower() == 'on')
    return
  
  def do_command_it(self, args):
    self.write('<p><dt>\n')
    self.do_remain(args)
    self.write('<dd>\n')
    return
  
  def do_command_pq(self, args):
    self.write('<div>\n')
    self.do_remain(args)
    self.write('</div>\n')
    return
  
  def do_command_an(self, args):
    self.write('<address>\n')
    self.do_remain(args)
    self.write('</address>\n')
    return

  do_command_pf = do_remain
  
  def do_command_do(self, args):
    self.write('<blockquote>\n')
    self.do_remain(args)
    return
  
  def do_command_dc(self, args):
    self.write('</blockquote>\n')
    self.do_remain(args)
    return

  def do_command_xr(self, args):
    s = name = args.pop(0)
    if args:
      s += ' (%s)' % args.pop(0)
    if name in self.XREF:
      self.write('<a href="%s.html"><span class="xr">%s</span></a>' % (name,s))
    else:
      self.write('<span class="xr">%s</span>' % s)
    self.do_remain(args)
    self.write('\n')
    return
  
  def do_command_pp(self, args):
    self.write('\n<p>\n')
    return
  
  def do_command_qq(self, args):
    self.write('"%s"' % ' '.join(args))
    return
  
  def do_command_dq(self, args):
    self.write('"%s"' % ' '.join(args))
    return
  
  def do_command_nm(self, args):
    if args:
      if not self.name:
        self.name = args.pop(0)
        self.write('<div class="name">%s</div>\n' % self.name)
      else:
        self.write('<code><span class="nm">%s</span></code>\n' % args.pop(0))
      self.do_remain(args)
    else:
      self.write('<code><span class="nm">%s</span></code>\n' % self.name)
    return
  
  def do_command_cm(self, args):
    self.write('<span class="config"><code>%s</code></span>' % ' '.join(args))
    return
  
  def do_command_bl(self, args):
    if 'indent' in args:
      self.write('<blockquote>\n')
      self.push('</blockquote>\n')
    else:
      self.write('<dl>\n')
      self.push('</dl>\n')
    return
  
  def do_command_el(self, args):
    self.write(self.state)
    self.pop()
    return
  
  def do_command_bd(self, args):
    self.write('<blockquote><pre>')
    return
  
  def do_command_ed(self, args):
    self.write('</pre></blockquote>\n')
    return
  
  def do_command_ic(self, args):
    self.write('<div class="cmdline"><kbd>')
    self.write(args.pop(0)+' ')
    self.do_remain(args)
    self.write('</kbd></div>\n')
    return

  do_command_dl = do_command_ic
  
  def do_command_pa(self, args):
    self.write('<span class="file"><code>%s</code></span>' % ' '.join(args))
    return
  
  def do_command_rs(self, args):
    self.write('<ul><li>\n')
    return
  
  def do_command_re(self, args):
    self.write('</ul>\n')
    return
  
  def do_command_p_r(self, args):
    self.write(' '.join(args)+' ')
    return
  
  def do_command_p_t(self, args):
    self.write(' <span class="cite">"%s"</span> ' % ' '.join(args))
    return
  
  def do_command_p_d(self, args):
    self.write(' '.join(args)+' ')
    return
  
  do_command_p_o = do_command_p_d
  do_command_p_n = do_command_p_d
  do_command_p_a = do_command_p_d

  do_command_ns = do_remain
  do_command_no = do_remain
  do_command_xo = do_remain
  do_command_ox = do_remain
  
  def do_command_ip(self, args):
    self.write('IP') # UGLY!
    self.do_remain(args)
    return
  
  def do_command_ql(self, args):
    self.write(' <kbd>%s</kbd> ' % ' '.join(args))
    return
  
  def do_command_ux(self, args):
    self.write('Unix')
    return
  
  def do_command_sq(self, args):
    self.write(' `<kbd>%s</kbd>\' ' % ' '.join(args))
    return
  
  def do_command_dv(self, args):
    self.write('<kbd>%s</kbd>' % ' '.join(args))
    return
  
  def do_command_li(self, args):
    self.write('<code>%s</code>' % ' '.join(args))
    return
  
  def do_command_aq(self, args):
    self.write('&lt;%s&gt;' % ' '.join(args))
    return
  
  def do_command_em(self, args):
    self.write('<strong>%s</strong>' % ' '.join(args))
    return
  
  def do_command_sx(self, args):
    s = ' '.join(args)
    self.write('<a href="#%s">%s</a>' % (s,s))
    return


# main
def main(argv):
  import getopt
  def usage():
    print 'usage: %s [-d] [-s version] [-c encin] [-C encout] [file ...]' % argv[0]
    return 100
  try:
    (opts, args) = getopt.getopt(argv[1:], 'ds:c:C:')
  except getopt.GetoptError:
    return usage()
  encin = 'euc-jp'
  encout = 'utf-8'
  for (k, v) in opts:
    if k == '-d': debug += 1
    elif k == '-s': version = v
    elif k == '-c': encin = v
    elif k == '-C': encout = v
  date = time.strftime('%Y/%m/%d')
  title = u'<a href="http://www.openssh.com/ja/">OpenSSH</a>-%s 日本語マニュアルページ (%s)' % (version, date)
  parser = Roff2HTML(title, sys.stdout, encout)
  for fname in (args or ['-']):
    if fname == '-':
      fp = sys.stdin
    else:
      fp = file(fname)
    parser.feedfile(fp, encoding=encin)
    fp.close()
  parser.close()
  return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
