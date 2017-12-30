.PHONY: build
build:
	cd site && jekyll build
	@echo "Open $$PWD/site/_site/index.html"

.PHONY: update-releases-json
update-releases-json:
	curl https://api.github.com/repos/fish-shell/fish-shell/releases \
	  | ./tools/update_release_metadata.py \
      > ./site/_data/releases.json

.PHONY: new-release
new-release: update-releases-json rebuild

clean:
	cd site && jekyll clean
