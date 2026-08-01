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

## Ecosystem openness

The JVM ecosystem is vast and multi-language. This skill provides defaults,
not a closed list. When encountering a tool or convention not covered here:

- inspect the project's `pom.xml`, `build.gradle(.kts)`, `build.sbt`,
  `deps.edn`, or `build.gradle` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
