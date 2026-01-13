push:
	sed -i '' '3s/.*/version = "$(version)"/' pyproject.toml
	python3 -m build
	python3 -m twine upload --repository pypi dist/techtrash_comfyapi-$(version)*

	git add .
	git commit -m "Bump version to $(version) : $(commit_message)"
	git push origin main