install:
	python setup.py develop
	pip install -r requirements.txt --use-mirrors

tests: install
	python run_tests.py --with-specplugin

coverage: install
	python run_tests.py --with-coverage --cover-package=url_tracker \
	 		    --with-specplugin --no-spec-color \
			    --cover-html --cover-html-dir=coverage

travis: coverage
	coveralls

.PHONY: install tests travis coverage
