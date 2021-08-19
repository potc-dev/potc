PLUGINS   := $(shell find $(shell ls) -maxdepth 0 -type d -name 'potc_*')
FORCE_CMD := $(if ${FORCE},--force-reinstall,)
DEV_CMD   := $(if ${DEV},--editable,)

list:
	@echo ${PLUGINS}

install:
	for p in ${PLUGINS}; do \
		pip install ${FORCE_CMD} ${DEV_CMD} `readlink -f $$p`; done

uninstall:
	for p in ${PLUGINS}; do \
		pip uninstall $$p -y; done
