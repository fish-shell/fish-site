---
layout: post
title: "What's happening with fish releases?"
date: 2023-05-27
categories: general
---

Here is a quick update on fish development and the plans for a new release.

Earlier this year, the fish committers agreed to undertake a significant rework
of the fish source code. In particular, efforts are underway to change the C++
core of fish to Rust. There are several reasons for this rewrite, including that
it enables development of a concurrent execution mode to allow background
execution of fish functions and related benefits. There's an [extended
discussion on GitHub](https://github.com/fish-shell/fish-shell/pull/9512), if
you're interested.

However, this is a process that is likely to take six months or more. In that
time the source tree will probably not be suitable for general release. The
performance of the partially-rewritten program is worse and building it is more
complicated. [Development
builds](https://github.com/fish-shell/fish-shell/wiki/Development-builds) are
currently not being generated because they're frankly more trouble than they're
worth.

The process is going reasonably well, with about 20% of the C++ code
removed in the last few months (as I measure it anyway). However, my
estimate is that it will not be ready for beta testing until late 2023
at the earliest.

There's a [handful of fixes for fish
3.6.1](https://github.com/fish-shell/fish-shell/issues?q=milestone%3A%22fish+3.6.2%22) that I think are worth rolling
up and [making a 3.6.2
release](https://github.com/fish-shell/fish-shell/discussions/9684) for, though I don't have a specific
timeline for doing so.

Hope that helps keep you informed!

David Adam &lt;[zanchey@](https://github.com/zanchey)&gt;<br>
fish committer
