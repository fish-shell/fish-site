# Contributing Guidelines

You can edit the main page, the tutorial, the 404 page, and assets (e.g. CSS, JS, images) from this repo,
they're all in [`site/`](site).

If you're making changes to the documentation, FAQ, design document, or something similar, don't edit [`docs/`](site/docs/).  
Instead, fork the [fish-shell repo](https://github.com/fish-shell/fish-shell) and make the changes in [`doc_src/`](https://github.com/fish-shell/fish-shell/blob/master/doc_src/).
The raw source of the documentation lives there.

The fish site is built via the Jekyll static site generator. Jekyll is used to populate the site with release versions, dates, tarballs, based on data from [the releases API](https://api.github.com/repos/fish-shell/fish-shell/releases). You will need to [install jekyll](https://jekyllrb.com), `gem install jekyll bundler` should do it.

## Building the site

1. Make the change in `site/`
2. Run `make` from the top level directory.
3. Open `docs/index.html` to see your change.

##  Making a new release

This assumes that the relevant release has been published in the [fish-shell github page](https://github.com/fish-shell/fish-shell/releases). These steps could obviously stand more automation.

1. Update the docs
    1. From the tarball, copy `user_doc/html` to the `site/docs/` directory.
    2. Name it with the proper major version number only (e.g. 2.7). The minor version number is omitted.
    3. `current` is just a copy of the most recent docs.  Delete `current` and replace it with a copy of the new directory.
2. Run `make new-release`. This downloads `releases.json` and rebuilds the site using it.
3. Open `docs/index.html` and check it. In particular ensure the tarball and Mac download links work.

## Publish the site

The site is hosted via GitHub pages with a custom domain. The site is served out of the `docs` directory.

After building the site (see above), do the following:

1. `git make` to build the site.
2. `git commit` your changes to `master`. Ensure the site is checked in.
4. `git push`

The public site will update immediately.
