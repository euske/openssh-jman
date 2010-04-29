# for GNU make only!

# Makefile for Japanese OpenSSH manpage
# by Yusuke Shinyama <yusuke @ cs . nyu . edu>
# $Id$

PACKAGE=openssh-jman
VERSION=550p1

GNUTAR=tar
SVN=svn
PYTHON=python
ROFF2HTML=$(PYTHON) roff2html.py

WORKDIR=/tmp
DISTNAME=$(PACKAGE)-$(VERSION)
DISTFILE=$(DISTNAME).tar.gz

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

.1.html:
	$(ROFF2HTML) $< > $@
.5.html:
	$(ROFF2HTML) $< > $@
.8.html:
	$(ROFF2HTML) $< > $@

# Maintainance:

$(WORKDIR)/$(DISTFILE): clean
	$(SVN) cleanup
	$(SVN) export . $(WORKDIR)/$(DISTNAME)
	$(GNUTAR) c -z -C$(WORKDIR) -f $(WORKDIR)/$(DISTFILE) $(DISTNAME) --dereference --numeric-owner
	rm -rf $(WORKDIR)/$(DISTNAME)

commit: clean
	$(SVN) commit

WEBDIR=$$HOME/Site/unixuser.org/doc/openssh/jman/
publish: $(WORKDIR)/$(DISTFILE) $(HTML)
	cp $(HTML) $(WORKDIR)/$(DISTFILE) $(WEBDIR)
	cp index.html $(WEBDIR)/index.html
