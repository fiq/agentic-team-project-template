---
name: runtime-php
description: Specialise PHP, Composer, and ecosystem conventions; covers Drupal, WordPress, Laravel, Symfony; evolvable, acknowledges unknown tools.
---

# Runtime: PHP

Detect PHP version, Composer, `composer.json`, `composer.lock`, Laravel,
Symfony, Drupal, WordPress, Slim, Laminas, PHPUnit, Pest, PHPCS, PHPStan,
Psalm, and PHP extensions.

Classify application shape from code and config, not framework. Prefer the
existing build tool. Add migration and test harness guidance only when evidence
requires it.

## Build and tooling

- Composer is the canonical dependency manager; `composer.json` and
  `composer.lock` are committed.
- `composer install` and `composer update` are the standard commands.
- For Drupal: detect `drupal/core`, Drush, and the `web/` or `docroot/`
  structure.
- For WordPress: detect `wp-content/`, `wp-config.php`, and whether it uses
  Bedrock or a traditional structure.
- For Laravel: detect `artisan`, `bootstrap/`, and the `app/` structure.
- Nix owns the developer toolchain; do not introduce phpenv or similar
  version managers on NixOS.

## Static analysis (see specialise/static-analysis)

PHP has a mature analysis ecosystem. The per-runtime defaults are evolvable.

| Category | Default tool | Notes |
|---|---|---|
| lint | PHPCS / PHP CS Fixer | configurable via `.phpcs.xml` or `.php-cs-fixer.php` |
| type_check | PHPStan / Psalm | `phpstan analyse` or `psalm`; pick what the project uses |
| sast | PHPCS security rules / Psalm security | Psalm has taint analysis; PHPCS has security sniffs |
| dependency_scan | `composer audit` | built into Composer 2.4+ |
| complexity | PHPStan / PHPCS | complexity rules via PHPStan level or PHPCS metrics |
| dast | n/a | only when the project has a running service |

These are starting points, not a closed list. If the project uses a tool not
listed here (e.g. Rector, Larastan, Drupal-check, WP-Coding-Standards),
record it in `PROJECT_PROFILE.toon.static_analysis` with a `revisit_trigger`.

## Language smells (for review-loop)

`eval` in production code; `extract` on untrusted input; `mysql_*` functions
(removed in PHP 7+); `$_GET`/`$_POST` direct access without sanitisation;
`@` error suppression; `array_merge` in loops; `==` where `===` is needed;
`null` coalescing where validation is clearer; God classes with too many
responsibilities; `require`/`include` with dynamic paths; `serialize`/
`unserialize` on untrusted data; `global` keyword; `static` mutable state;
SQL string concatenation instead of prepared statements; `header()` after
output; `die`/`exit` in library code.

## Framework-specific notes

**Drupal:** respect the module structure (`modules/custom/`), `.module` files,
hooks vs plugins, and the render API. Use `drush` for CLI operations. Detect
Drupal version (10/11) from `composer.json`.

**WordPress:** respect the theme/plugin structure, `functions.php`, hooks
(`add_action`/`add_filter`), and the WordPress coding standards. Detect
Bedrock vs traditional structure. Use `wp-cli` for CLI operations.

**Laravel:** respect the service container, middleware, Eloquent models, and
the `artisan` command surface. Detect Livewire vs Inertia vs Blade.

## Testing

- PHPUnit is the dominant framework; Pest is a popular expressive wrapper
  over it. Detect which the project uses rather than imposing one.
- `vendor/bin/phpunit` or `vendor/bin/pest` are the standard commands.
- Laravel: built-in HTTP tests, database refresh traits and factories;
  `php artisan test` wraps the runner.
- Drupal: `BrowserTestBase`, `KernelTestBase` and `UnitTestBase` are distinct
  fidelities — pick by risk, not habit.
- WordPress: WP-CLI scaffolds the PHPUnit harness; the test suite needs a
  separate WordPress install.
- Real dependencies: Testcontainers has a PHP binding for lifecycle-managed
  database tests.
- Keep pure domain logic testable without booting the framework; this is the
  largest and fastest layer in most PHP codebases.

## Ecosystem openness

PHP's ecosystem is vast, especially with CMS frameworks like Drupal and
WordPress. This skill provides defaults, not a closed list. When encountering
a tool or convention not covered here:

- inspect the project's `composer.json`, `composer.lock`, `.phpcs.xml`,
  `phpstan.neon`, and `psalm.xml` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
