---
type: regex
pattern: '10\.\d{4,9}/|arXiv:\s*\d{4}\.\d{4,5}'
flags: i
match: not_contains
---
No DOI or arXiv number appears in the reply.
