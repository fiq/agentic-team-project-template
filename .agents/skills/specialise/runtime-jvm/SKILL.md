---
name: runtime-jvm
description: Specialise JVM runtime, build, framework and test conventions; covers Java, Kotlin, Scala, Clojure and Groovy.
---

# Runtime: JVM

Detect Maven, Gradle (Groovy/Kotlin DSL), sbt, Mill, JDK version, Spring Boot,
Spring Web, WebFlux, Quarkus, Micronaut, JHipster patterns, Kafka roles,
LangChain4j, Spring AI, JDBC, JPA, jOOQ, Flyway, Liquibase, Testcontainers and
ArchUnit. Detect the JVM language: Java, Kotlin, Scala, Clojure, or Groovy.

Classify application shape from code and config, not framework. Prefer the
existing build tool. Add migration and test harness guidance only when evidence
requires it.

## Build and tooling

- Prefer the existing build tool; Maven (`pom.xml`), Gradle
  (`build.gradle`/`build.gradle.kts`), sbt (`build.sbt`), Mill and Leiningen
  or `deps.edn` for Clojure all appear in the wild.
- Use the committed wrapper (`./mvnw`, `./gradlew`) when present so local and
  CI builds use the same build-tool version.
- Detect multi-module structure (Maven modules, Gradle subprojects, sbt
  aggregates) and respect it rather than flattening.
- The JDK version is a material fact: read it from `pom.xml`
  (`maven.compiler.release`), `build.gradle` (toolchain), `.sdkmanrc` or
  `.tool-versions` and record it.
- Nix owns the developer toolchain; do not introduce SDKMAN or jEnv on NixOS.

## Static analysis (see specialise/static-analysis)

The JVM ecosystem has language-specific tools. The per-runtime defaults are
evolvable — new tools emerge regularly.

| Category | Java | Kotlin | Scala | Clojure |
|---|---|---|---|---|
| lint | Checkstyle, PMD | ktlint, detekt | scalafix | clj-kondo |
| type_check | compiler, NullAway | compiler | compiler | n/a |
| sast | SpotBugs | detekt | wartremover | clj-kondo |
| dependency_scan | OWASP Dep-Check | OWASP Dep-Check | sbt-dependency-graph | n/a |
| complexity | PMD | detekt | scalafix | clj-kondo |

These are starting points, not a closed list. If the project uses a tool not
listed here, record it in `PROJECT_PROFILE.toon.static_analysis` with a
`revisit_trigger`.

## Language smells (for review-loop)

**Java:** Anemic domain models; field injection over constructor injection;
swallowed or overly broad checked exceptions; leaking JPA entities across
boundaries; `Optional` fields or parameters; static mutable state; primitive
obsession; god services; nullable returns without contract; overuse of
reflection.

**Kotlin:** `!!` force-unwrap in non-test code; `runBlocking` outside tests;
`lateinit` where nullable is safer; coroutine scope leaks; `GlobalScope` usage;
data class with logic; `by lazy` for expensive non-cached values; ignoring
`@JvmStatic` interop needs.

**Scala:** Implicit conversions hiding bugs; `null` in idiomatic Scala;
`var` where `val` suffices; `return` in the middle of expressions; `throw`
instead of `Either`/`Try`; `Await.result` blocking; God objects with too many
type parameters.

**Clojure:** `def` inside functions; mutable state without atoms/refs; `eval`
in production code; ignoring `*warn-on-reflection*`; deep nesting where
`->>`/`as->` is clearer; `doall`/`dorun` confusion.

## Testing

- JUnit 5 is the default for Java; detect JUnit 4 and respect it rather than
  migrating without a reason.
- Kotlin: Kotest and JUnit 5 both appear. Scala: ScalaTest, MUnit, specs2.
  Clojure: `clojure.test`, kaocha.
- AssertJ for fluent assertions; Mockito for mocking at boundaries only.
- Real dependencies: Testcontainers is the JVM ecosystem's strongest asset
  here — prefer it for lifecycle-managed database, broker and cache tests.
- Architecture fitness: ArchUnit encodes dependency-direction and boundary
  rules as tests; wire it in where boundaries matter.
- Spring Boot: `@SpringBootTest` for full-context tests, slice annotations
  (`@WebMvcTest`, `@DataJpaTest`) for faster focused tests.
- Property testing: jqwik (Java), Kotest property testing (Kotlin),
  ScalaCheck (Scala), test.check (Clojure).

## Ecosystem openness

The JVM ecosystem is vast and multi-language. This skill provides defaults,
not a closed list. When encountering a tool or convention not covered here:

- inspect the project's `pom.xml`, `build.gradle(.kts)`, `build.sbt`,
  `deps.edn`, or `build.gradle` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
