
.PHONY: new_release
new_release:
	# Download releases JSON file
	curl https://api.github.com/repos/fish-shell/fish-shell/releases \
	  | ./tools/update_release_metadata.py \
      > ./site/_data/releases.json
	# Run jekyll
	cd site && jekyll build
	@echo "Open $$PWD/site/_site/index.html"

clean:
	cd site && jekyll clean
