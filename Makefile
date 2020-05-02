install:
	pip install -r requirements.txt

deploy-stag:
	fab deploy --instance=staging

deploy-prod:
	fab deploy --instance=production

backup-stag:
	fab backup --instance=staging

backup-prod:
	fab backup --instance=production
