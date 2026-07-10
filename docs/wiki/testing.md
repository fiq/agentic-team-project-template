# Testing

Prefer a testing trophy:

```
                         E2E
                          /\
                         /few\
                       /------\
                      /component\
                    /integration\
                   /------------\
                  / contract     \
                 /----------------\
                / unit/domain      \
               /____________________\
```

Use real dependencies where semantics matter and cost is reasonable. Do not let
mocked tests overclaim confidence.
