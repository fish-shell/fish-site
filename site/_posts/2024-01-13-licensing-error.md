---
layout: post
title: "Incomplete licensing information in previous fish releases"
date: 2024-01-13
categories: general
---

During the work on fish 3.7.0, we discovered that the licensing
information in the documentation for some of the derived code contained in
fish had been removed during the work on fish 3.1.0, and that this was not
corrected until the release of fish 3.7.0. Although the source contained
the correct licensing information, this was not published as part of the
release's documentation.

In particular, fish 3.1.0-3.6.4 contain:
* Code derived from CMake under the BSD license
* Code derived from OpenBSD & tmux under the OpenBSD license
* Code derived from glibc under the LGPL
* UTF-8 code by Alexey Vatchenko under the ISC license
* Code from NetBSD under the NetBSD license
* Code from AngularJS/Google under the MIT license

While these are noted in the source code, the user-visible documentation
does not contain an appropriate acknowledgement.

We regret the error. It was discovered during a routine audit of the code
and documentation for fish, which will occur during the release cycle on
an ongoing basis.
