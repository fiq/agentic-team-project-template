---
name: runtime-ruby
description: Specialise Ruby, Bundler, and ecosystem conventions; evolvable, acknowledges unknown tools.
---

# Runtime: Ruby

Detect Ruby version, Bundler, Gemfile, Rake, Rails, Sinatra, Hanami, Roda,
Sidekiq, Resque, ActiveRecord, Sequel, RSpec, Minitest, Sorbet, and
Solid Queue.

Classify application shape from code and config, not framework. Prefer the
existing build tool. Add migration and test harness guidance only when evidence
requires it.

## Build and tooling

- Bundler is the canonical dependency manager; `Gemfile` and `Gemfile.lock` are
  committed.
- `bundle exec` is the standard prefix for running commands in the bundle
  context.
- Rake is the default task runner; detect and respect existing `Rakefile`.
- Version managers (rbenv, rvm, asdf) are common in the wild; on NixOS, do not
  introduce them — Nix owns the toolchain.

## Static analysis (see specialise/static-analysis)

Ruby has a mature analysis ecosystem. The per-runtime defaults are evolvable.

| Category | Default tool | Notes |
|---|---|---|
| lint | RuboCop | configurable via `.rubocop.yml` |
| type_check | Sorbet (if adopted) | `srb tc`; only when the project uses Sorbet |
| sast | Brakeman | security scanner for Ruby on Rails |
| dependency_scan | bundler-audit | `bundle audit check` |
| complexity | RuboCop | complexity cops (Metrics/*) |
| dast | n/a | only when the project has a running service |

These are starting points, not a closed list. If the project uses a tool not
listed here (e.g. StandardRB, reek, fasterer, rubocop-rspec, rubocop-rails),
record it in `PROJECT_PROFILE.toon.static_analysis` with a `revisit_trigger`.

## Language smells (for review-loop)

`nil` checks where `&.` or `fetch` is safer; `rescue Exception` swallowing
errors; `instance_variable_get`/`set` in non-metaprogramming code; `eval` in
production code; `String#+` in loops instead of `Array#join`; `each` where
`map`/`select`/`reduce` is clearer; mutable default arguments (`def f(x=[])`);
`self.` where implicit receiver is clearer; God classes with too many
responsibilities; `before`/`after` blocks in specs that should be `let`;
`subject` overuse where named variables are clearer; `should` syntax in RSpec
(old style); `attr_accessor` where `attr_reader` suffices.

## Testing

- RSpec is the most common test framework; Minitest is also widely used.
- `bundle exec rspec` or `bundle exec rake test` are the standard commands.
- FactoryBot for test data; Faker for generated values.
- System tests may use Capybara with Selenium or Cuprite.
- Respect the existing test framework; do not impose a different one.

## Ecosystem openness

Ruby's ecosystem evolves. This skill provides defaults, not a closed list.
When encountering a tool or convention not covered here:

- inspect the project's `Gemfile`, `Gemfile.lock`, `.rubocop.yml`,
  `.ruby-version`, and `Rakefile` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
