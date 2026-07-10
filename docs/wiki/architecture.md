# Architecture

Use the smallest architecture that satisfies evidence and intent.

```
external world -> adapters -> use cases -> domain/application
                                    ^
                                    |
                         dependency direction
```

Add boundaries around volatile external APIs, databases, brokers, object
storage, payment providers, AI model providers and cloud-specific services when
they materially affect behaviour or tests.

Do not create one interface per class.
