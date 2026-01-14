VERSION = 0.6.0rc2



version:
	echo "version = '$(VERSION)'" > airflow_dbt/__version__.py
	 
tag:
	echo "version = '$(VERSION)'" > airflow_dbt/__version__.py
	git add -u  
	git commit -m "tag: v$(VERSION)"
	git tag v$(VERSION)
	git push --tags

build:
	@rm -rf dist
	@uv build -o dist


publish:	
	@uv publish 
 
	

all: tag build publish
