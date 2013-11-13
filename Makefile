# for GNU make only!

# Makefile for Japanese OpenSSH manpage
# by Yusuke Shinyama <yusuke at cs . nyu . edu>

PACKAGE=openssh-jman
VERSION=6.4p1
VERSION2=640p1

RM=rm -f
CP=cp -f
TAR=tar
PYTHON=python
ROFF2HTML=$(PYTHON) roff2html.py -s $(VERSION)

DISTNAME=$(PACKAGE)-$(VERSION2)
DISTFILE=/tmp/$(DISTNAME).tar.gz

#
.SUFFIXES: .0 .1 .2 .3 .4 .5 .6 .7 .8 .9 .html

#
SRCS=scp.1 sftp-server.8 sftp.1 ssh-add.1 ssh-agent.1 ssh-keygen.1 ssh-keyscan.1 \
	ssh.1 sshd.8 ssh-keysign.8 ssh_config.5 sshd_config.5 ssh-pkcs11-helper.8

HTML=scp.html sftp-server.html sftp.html ssh-add.html \
	ssh-agent.html ssh-keygen.html ssh-keyscan.html ssh.html \
	sshd.html ssh-keysign.html ssh_config.html sshd_config.html ssh-pkcs11-helper.html

all: $(HTML)

clean: 
	-$(RM) $(HTML)
	-$(RM) $(DISTFILE)

.1.html:
	$(ROFF2HTML) $< > $@
.5.html:
	$(ROFF2HTML) $< > $@
.8.html:
	$(ROFF2HTML) $< > $@

# Maintainance:

archive: $(DISTFILE)
$(DISTFILE): clean
	$(TAR) zcf $(DISTFILE) $(SRCS) roff2html.py Makefile README.txt

WEBDIR=$$HOME/work/Site/unixuser.org/doc/openssh/jman/
publish: $(DISTFILE) $(HTML)
	$(CP) $(HTML) $(DISTFILE) $(WEBDIR)
	$(CP) index.html $(WEBDIR)/index.html
