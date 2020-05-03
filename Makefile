install:
	pip install -r requirements.txt

deployst:
	fab deploy --instance=staging

deploypr:
	fab deploy --instance=production

deploy:
	fab deploy --instance=staging
	fab deploy --instance=production

backupst:
	fab backup --instance=staging

backuppr:
	fab backup --instance=production

backup:
	fab backup --instance=staging
	fab backup --instance=production

