# Filled by debhelper scripts when constructing the package
DESTDIR=

# Commands aliases
INSTALL=install -m 0644
INSTALL_BIN=install -m 0755
CREATE_DIR=install -d -m 0755

# Install details
PLUGIN=license_manager
PLUGIN_INSTALLDIR=$(DESTDIR)/opt/faurecia/plugins/${PLUGIN}

# Files
BIN=check_*.py
DATA=LICENSE Changes
CONF=config.py

default:

install: clean install_dirs
	${INSTALL_BIN} ${BIN} ${PLUGIN_INSTALLDIR}
	${INSTALL} ${CONF} ${PLUGIN_INSTALLDIR}
	${INSTALL} ${DATA} ${PLUGIN_INSTALLDIR}
	${INSTALL} nagios/* ${PLUGIN_INSTALLDIR}/nagios
	${INSTALL} backend/* ${PLUGIN_INSTALLDIR}/backend

install_dirs:
	${CREATE_DIR} ${PLUGIN_INSTALLDIR}
	${CREATE_DIR} ${PLUGIN_INSTALLDIR}/nagios
	${CREATE_DIR} ${PLUGIN_INSTALLDIR}/backend

clean:
	@echo 'Cleaning Python byte code files...'
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	
	@echo 'Cleaning backup files...'
	@find . -name '*~' -exec rm -f {} +
	@find . -name '#*#' -exec rm -f {} +

