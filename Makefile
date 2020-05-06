install:
	pip install -r requirements.txt

deployproduction:
	fab deploy --instance=production

deploy:
	fab deploy --instance=staging

backup:
	fab backup --instance=production

