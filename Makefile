RES_DIR = 'src/view/res'
QM_DIR = 'src/view/res/l10n'
TS_DIR = 'l10n'
PRO_FILE = 'MetaTerm.pro'

.PHONY: update_resources
update_resources:
	cd $(RES_DIR) && \
	pyrcc4 -py3 resources.qrc > resources.py

.PHONY:update_l10n
update_l10n:
	pylupdate4 $(PRO_FILE)

.PHONY:release_l10n
release_l10n:
	cd $(TS_DIR) && \
	for file in *.ts; \
		do lrelease-qt4 "$$file" -qm ../$(QM_DIR)/`basename "$$file" .ts`.qm; \
	done; \
