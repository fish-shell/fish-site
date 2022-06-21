.PHONY: build
build:
	cd site && jekyll build --destination ../docs/
	@# Sphinx likes to put stuff in _static and _sources.
	@# Jekyll will strip these out except for a whitelist,
	@# which has no glob capability and would need to be
	@# updated every release.
	@# So just copy the docs directory entirely.
	rsync --recursive --exclude '.*' site/docs/ ./docs/docs/
	touch ./docs/.nojekyll
	@echo "Open $$PWD/docs/index.html"

.PHONY: update-releases-json
update-releases-json:
	curl https://api.github.com/repos/fish-shell/fish-shell/releases \
	  | ./tools/update_release_metadata.py \
      > ./site/_data/releases.json

.PHONY: new-release
new-release: update-releases-json build

clean:
	cd site && jekyll clean
