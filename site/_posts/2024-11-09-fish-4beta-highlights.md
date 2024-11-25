---
layout: post
title: "Highlights and under-the-hood look at fish 4.0"
date: 2024-11-09
categories: general
---

<!--toc:start-->
- [Why fish](#why-fish)
- [Terminal Support](#terminal-support)
- [Under the Hood](#under-the-hood)
  - [Why port from C++ to Rust](#why-port-from-c-to-rust)
  - [Porting Process](#porting-process)
  - [Development Papercuts](#development-papercuts)
  - [Code Review](#code-review)
  - [git bisect](#git-bisect)
  - [git blame](#git-blame)
- [Wrap-up](#wrap-up)
- [Footnotes](#footnotes)
<!--toc:end-->

## Why fish

Unix shell scripts are remarkably useful for all kinds of everyday tasks.
I love using [POSIX shell](https://pubs.opengroup.org/onlinepubs/9799919799/idx/shell.html),
a small and beautiful lingua franca that has been around for decades.
As many of my scripts are written in the hope they will be read,
modified or executed by other people,
this standardized language is a great fit for me.
Shell scripts are super concise,
sometimes even better for human communication than prose[^tutorial] -- definitely less ambiguous.

In addition to running all commands in a script file in batch mode, a shell can also run interactively,
repeatedly prompting the user for the command to execute next.

fish is a shell that aims to improve the interactive experience of composing and executing commands.
I've been using it for about 10 years,
I think I initially switched for features like autosuggestions
which made it seem better than the competition.

fish provides an intuitive UI with:

- autosuggestion
- tab-completion[^autocompletion]
- syntax highlighting
- detailed error messages
- ways to recall and delete commands from history[^bash-history-search]
- keyboard shortcuts for common use cases[^keyboard-shortcuts]
- interactive editing of multi-line commands, with automatic indentation
- syntax that's not too alien to a user already familiar with Python[^syntax]
- commands and variables for customization

An overarching theme is that fish seeks to provide a good
default behavior for the average user.

Today fish lacks some of the convenient syntax found in POSIX shells;
my plan is to next add an opt-in mode enabling compatibility in most practical cases.
There are a some other shells with similar goals;
most come with a unique scripting language.

## Terminal Support

fish is in an excellent position to implement integrations for various new terminal features in a way that benefits many users.
We hope to be both contributing to and benefitting from future standardization.

Since fish is not usually preinstalled, it has a lot of incentive to play nice with other systems.
In the past fish has done some user-agent sniffing by enabling or disabling code based on `$TERM`.
We've removed a lot of these workarounds already,
to reduce surprise and encourages fixing bugs at the source,
which helps our peers that don't have our workarounds.

Among others, fish implements

- Operator System Command (OSC) 0 terminal title
- OSC 7 working directory reporting
- OSC 52 copy to clipboard
- OSC 133 prompt marking
- (partially) setting/restoring the terminal cursor
- (partially) focus reporting
- Parts of the [kitty keyboard protocol](https://sw.kovidgoyal.net/kitty/keyboard-protocol/)

## Under the Hood

The remaining sections look at the recent Rust port and some related topics regarding internal development.

### Why port from C++ to Rust

Fish was implemented in C++11 and has recently been ported to [Rust](https://www.rust-lang.org/).

I love C++.
Reading and writing C++ is like standing on the shoulders of giants.

Unfortunately, it seems to become increasingly hard to find C++ programmers motivated to work on shiny tools,
especially within fish's target audience.
fish is a project with a large scope, attempting to solve lots of UI problems by itself.
It is written by hundreds volunteers who, over the years have come and gone,
leaving behind a heterogenous code base.
Our low requirements on the quality of contributions enable growth but also add tech debt.
Mainstream programming styles have changed a lot since fish was initially written almost 20 years ago.
It doesn't help that we were stuck on the fairly old C++11 and afraid to upgrade for some reason.

It is definitely possible to make [basically finished software out of beautiful C++20](https://kakoune.org/)
but given fish's aspirations, historical baggage and present resources, that's unrealistic.

To enable the project to continue to grow at a solid pace, we
[ported it to Rust](https://github.com/fish-shell/fish-shell/pull/9512).
Rust has definitely become the language of choice for comparable projects.
Some highlights are its modern defaults, impressive standard library,
a coherent ecosystem and a great story on multi-threading[^multi-threading].

### Porting Process

This was an incremental port, using [cxx](https://cxx.rs/) and [autocxx](https://google.github.io/autocxx/) for interop.
These tools have known limitations, namely that function calls crossing the
foreign-function-interface (FFI) boundary can pass only certain types as arguments.

To port a piece of C++ code, the steps are:
1. Find all dependencies of the code, ideally port them first.
   Doing so avoids the need to call C++ functions from Rust,
   which can be tricky due to
   which might need work around limitations of the FFI.
2. Define the FFI for the ported code, that is, Rust functions that may be called from C++.
3. Port the code, implement any FFI shims in Rust and delete the C++ version.

This process was challenging the first few times, mostly because of the
subtleties involved in making the FFI calls work.

Once that's been figured out, it became mostly a boring routine task
because most C++ code was modest enough, that is, free of template metafunctions,
to have a direct Rust equivalent.
It was a lengthy process mostly due to the amount of code.
Porting larger chunks of code in one commit felt more productive, since that
reduces the amount of tricky FFI code to be written only to be thrown away.
Overall, it might have been worth to automate most of the repetitive steps.

### Development Papercuts

For historical reasons, fish internally encodes strings as UTF-32.
Pretty-printing these wide-strings doesn't work out-of-the box in [GDB](https://www.gnu.org/software/binutils/) unfortunately.
I haven't found that to be a big problem since there hasn't been much need for low-level debugging.

[rust-analyzer](https://rust-analyzer.github.io/) has mostly been working well.
Naturally it would fail to cross the language boundary and struggle when there are lots of compile errors.
In some scenarios, `rust-analyzer` consistently used too much memory (on a system with 16GB RAM), prompting me to configure my OOM daemon to kill it first.
Code Actions (usually rendered as 💡) are useful for boring code changes such as adding import statements,
and Code Lenses can be used to run unit tests.

### Code Review

To minimize risk, code changes should be reviewable (even if the author ends up being the only reviewer).
As a rule of thumb, code review effort scales quadratically with the size of the change.
Now porting a chunk of code from one language to another one is a noisy change but it's not "large" as in "hard to understand".
There are no logic changes, and, in our case, usually no significant changes to the syntax tree either.
This means that a code reviewer need not symbolically execute any new or changed code paths.
It's enough to do equivalence checking.
Humans speaking both C++ and Rust can do this at a high level with a simple linear scan through the changes,
checking the corresponding old and new statements for equivalence at each step.

You can probably count the number of regressions on [20k ported lines](https://github.com/fish-shell/fish-shell/commit/77aeb6a2a88af77077cc1c42b8a11c6b2a59d744) on one hand.
Our test suite is generally good but fails to cover a lot of interactive scenarios.
There were numerous regressions that were not caught by automated tests.
Fortunately, most of these didn't reach any user.

### git bisect

We use [`git bisect`](https://git-scm.com/docs/git-bisect) heavily to find the commit that introduced a regression.

### git blame

[Git commit discipline](https://github.com/git/git/blob/facbe4f633e4ad31e641f64617bc88074c659959/Documentation/SubmittingPatches#L234-L264) is great here[^commit-discipline].
This allows anyone to quickly run a few recursive [`git blame`](https://git-scm.com/docs/git-blame)
commands to figure out -- within mere seconds -- why any given piece of code was introduced.
In lieu of an equivalent automated test, this knowledge enables future contributors to make changes without fear of random breakage.

The [steps I use for recursive blaming](https://github.com/jonas/tig/pull/1316#discussion_r1488761119)
involve showing the diff of the blamed commit in my Git UI then running `git blame` again, on the old version of the interesting line.
This is repeated until I find the interesting change.
Inside such a diff, I I usually find the old version of a line by searching for parts of the line itself,
usually comments[^comments] because those tend to be unique.
Unrelated commits such as style changes can be skipped easily this way.
Same goes for commits that port code from C++ to Rust.
They do not generally make it significantly harder to search through the history.

This style of recursive Git blame works well with "continuous" commits,
where moved lines are created and deleted within the same commit;
That's one reason my interpretation [recipe style history](https://www.bitsnbites.eu/git-history-work-log-vs-recipe/) uses continuous commits.

A different school of thought puts the new (Rust) code into
one commit, to adopt it in a second commit, that also deletes the old C++ version.
Such commits can still be verified in isolation but not by mainly looking at the diff.
Instead, one can compare both versions by visiting the first commit's tree in their IDE, which enables code navigation.

## Wrap-up

If nothing else, the port was great for learning and has already payed
dividends in increased velocity.

There are some nice improvements coming up fish 4.0.
[Please test it](https://github.com/fish-shell/fish-shell/wiki/Development-builds)
if you feel so inclined. Thanks to everyone for reporting issues.

---

<p style="text-align: right">
Johannes
</p>

## Footnotes

[^tutorial]:
	Of course there is some barrier to entry.
	I remember [The Linux Command Line](https://www.linuxcommand.org/tlcl.php)
	being a very helpful set of tutorials.

[^autocompletion]:
	Curiously, there have been successful startups valued at millions of dollars for
	a product that adds smart autocompletion to your shell.

[^keyboard-shortcuts]:
	My favorite shortcut is `ctrl-x` which copies the command line to the system clipboard.

[^bash-history-search]:
	Bash sometimes get into a state where `ctrl-p` won't recall the last
	command but another one, I still need to figure out how to work around
	that, please help.

[^syntax]:
	It took me many years to consciously realize that quoted strings in shell can span multiple lines.
	It seems so obvious now, and super useful.

[^multi-threading]:
	The traditional Unix way to run some computation in the background is to spawn a separate process.
	For better or worse, fish uses operating system threads instead,
	for querying file metadata or performing history search.
	Multi-threading introduces very complex problems but Rust is definitely a hammer for those.
	It would be interesting to revisit this.
	Going multi-process instead of multi-threaded sounds attractive; it could allow users to
	define arbitrary programs to do background computations.

[^commit-discipline]:
	A reasonable commit history definitely makes hacking more fun,
	not in the least because it's correlated with people who are here for the long term.

[^comments]:
	Rather than writing comments in the source code, I often prefer putting
	the same information in commit messages instead.
	Commit messages can be more powerful since they can be found via any of the changed lines.
