---
name: runtime-perl
description: Specialise Perl and Raku runtime, build, and ecosystem conventions; evolvable, acknowledges unknown tools.
---

# Runtime: Perl / Raku

Detect Perl version, cpanm, Carton, Dist::Zilla, App::perlbrew, plenv, and
Raku (Rakudo, zef). Detect frameworks: Dancer, Mojolicious, Catalyst,
PSGI/Plack, and Raku frameworks (Croissant, Bailador).

Classify application shape from code and config, not framework. Prefer the
existing build tool. Add migration and test harness guidance only when evidence
requires it.

## Static analysis (see specialise/static-analysis)

The Perl/Raku ecosystem has established analysis tools. The per-runtime
defaults are evolvable.

| Category | Perl | Raku |
|---|---|---|
| lint | perlcritic | Raku native warnings |
| type_check | n/a | n/a |
| sast | Perl::Critic security policies | n/a |
| dependency_scan | cpm audit / CPAN audit | zef list --installed |
| complexity | perlcritic (complexity policies) | n/a |

These are starting points, not a closed list. If the project uses a tool not
listed here, record it in `PROJECT_PROFILE.toon.static_analysis` with a
`revisit_trigger`.

## Language smells (for review-loop)

**Perl:** `use strict`/`use warnings` missing; barewords; `$@` after `eval`
without localisation; `defined` vs truthiness confusion; `@_` manipulation
instead of named parameters; global variables instead of lexicals; `unless`
blocks that are hard to read; `map`/`grep` in void context; regex without
`/x` for complex patterns; `open` without 3-arg form; `system` without list
form.

**Raku:** `say` without `use v6.d` (or later); `dd` left in production code;
`.so`/`.not` where explicit comparison is clearer; `EVAL` in production;
ignoring `Failure` return values; `Nil` where `Empty` is meant; deep metaop
chains that are unreadable.

## Ecosystem openness

Perl and Raku have long-lived ecosystems. This skill provides defaults, not a
closed list. When encountering a tool or convention not covered here:

- inspect the project's `cpanfile`, `dist.ini`, `Makefile.PL`,
  `Build.PL`, `META6.json`, or `zef.json` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
