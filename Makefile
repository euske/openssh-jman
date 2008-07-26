# for GNU make only!

# Makefile for Japanese OpenSSH manpage
# by Yusuke Shinyama <yusuke @ cs . nyu . edu>
# $Id: Makefile,v 1.5 2008/04/03 13:35:51 yusuke Exp $

VERSION=510p1

PYTHON=python
ROFF2HTML=$(PYTHON) roff2html.py

#
.SUFFIXES: .0 .1 .2 .3 .4 .5 .6 .7 .8 .9 .html

#
SRCS=scp.1 sftp-server.8 sftp.1 ssh-add.1 ssh-agent.1 ssh-keygen.1 ssh-keyscan.1 \
	ssh.1 sshd.8 ssh-keysign.8 ssh-rand-helper.8 ssh_config.5 sshd_config.5

HTML=scp.html sftp-server.html sftp.html ssh-add.html ssh-agent.html ssh-keygen.html ssh-keyscan.html \
	ssh.html sshd.html ssh-keysign.html ssh-rand-helper.html ssh_config.html sshd_config.html

all: $(HTML)

clean: 
	-rm $(HTML)

PACKAGE=openssh-jman-$(VERSION).tar.gz
pack: clean
	cd ..; tar c --exclude CVS --numeric-owner -z -f $(PACKAGE) jman

.1.html:
	$(ROFF2HTML) $< > $@
.5.html:
	$(ROFF2HTML) $< > $@
.8.html:
	$(ROFF2HTML) $< > $@

DESTDIR=$$HOME/public_html/doc/openssh/jman/
publish: pubhtml pubtgz
pubhtml: $(HTML)
	cp $(HTML) $(DESTDIR)
pubtgz: clean pack
	mv ../$(PACKAGE) $(DESTDIR)
