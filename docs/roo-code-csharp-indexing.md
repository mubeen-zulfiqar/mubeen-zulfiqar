# Roo Code: correcting C# captures for codebase indexing

**Contribution:** [RooCodeInc/Roo-Code #7813](https://github.com/RooCodeInc/Roo-Code/pull/7813)  
**Merged:** September 15, 2025  
**Scope:** C# Tree-sitter queries in the existing code-indexing pipeline

## Problem

The issue investigated in the pull request was C# code failing to receive the expected structured processing for codebase indexing. The investigation followed the path from language detection through Tree-sitter parsing and query captures to embedding generation.

## Change

I changed the C# queries so declaration names and their enclosing definitions were captured separately. For example, the class query changed from:

```scheme
(class_declaration
  name: (identifier) @name.definition.class)
```

to:

```scheme
(class_declaration
  name: (identifier) @name) @definition.class
```

The distinction is the node being captured: the identifier supplies the name, while the enclosing class supplies the full definition. The change was not a general prohibition on dots in Tree-sitter capture names.

The patch also added qualified-name alternatives alongside simple namespace names, including file-scoped namespaces, and adjusted captures for other C# constructs such as methods, properties, attributes, and type parameters.

## Evidence and verification

- The [merged diff](https://github.com/RooCodeInc/Roo-Code/pull/7813/files) shows the changes to `src/services/tree-sitter/queries/c-sharp.ts`.
- The PR documents my manual investigation, a C# sample, and testing on a project containing several hundred C# files. These are the verification steps reported in the PR, not a published benchmark or an independently reproduced evaluation.
- Upstream accepted the change on September 15, 2025. The PR links the related reports [#5238](https://github.com/RooCodeInc/Roo-Code/issues/5238) and [#6048](https://github.com/RooCodeInc/Roo-Code/issues/6048).

## Contribution boundary

This was a focused query correction within Roo Code's existing parsing and embedding infrastructure. I did not build the entire indexing system, and this case study makes no retrieval-quality, latency, or adoption claims.

[Back to profile](../README.md)
