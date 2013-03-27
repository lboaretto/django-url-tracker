install:
	pip install -e . -r requirements.txt

tests:
	python run_tests.py --with-specplugin

coverage:
	python run_tests.py --with-coverage --cover-package=url_tracker \
	 		    --with-specplugin --no-spec-color \
			    --cover-html --cover-html-dir=coverage

travis: coverage
	coveralls

.PHONY: install tests travis coverage
