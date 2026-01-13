# Globus Identity Mapper

The _Globus Identity Mapper_ Python library provides two mapping classes that
implement configurable hooks for mapping a Globus Auth Identity resource to
an application- or context-specific username:

- `ExpressionIdentityMapping`
- `ExternalIdentityMapping`

Additionally, the library offers a protocol for implementing custom identity
mapper logic:

- `IdentityMappingProtocol`

Most consumers of this library will make use of a mapping configuration
document, the `.from_mapping_document()` method to instantiate the appropriate
class, and then call `.map_identity()` or `.map_identities()` thereafter.
This enables administrators to dynamically specify their desired mapping
configuration without having to resort to typing Python code.  For example, a
simple mapping configuration to use the `ExpressionIdentityMapping` logic to
follow the rules as documented at [Globus Connect Server, Identity Mapping](
https://docs.globus.org/globus-connect-server/v5.4/identity-mapping-guide/)
might be:

```json
{
  "DATA_TYPE": "expression_identity_mapping#1.0.0",
  "mappings": [
    {
      "source": "{email}", "match": "(.*)@example\\.org", "output": "{0}"
    }
  ]
}
```

A hard-coded class instantiation might look like:

```python
>>> import json
>>> from globus_identity_mapping import ExpressionIdentityMapping
>>> fdata = open("example_configuration.json").read()
>>> mapping_document = json.loads(fdata)
>>> connector_id = "..."  # see the Identity Mapping Guide, linked above
>>> storage_gateway = "application-specific-identifier"
>>> mapper = ExpressionIdentityMapping.from_mapping_document(
...   mapping_document, storage_gateway=storage_gateway, connector_id=connector_id
... )
```

Thereafter, the `mapper` may be used to find a context-aware username by
mapping the source field of `email` from a Globus Auth Identity record via
the regular expression logic.  (In the above example, the hostname is stripped
to determine the application-specific username.)  Example:

```python
>>> gair = {"id": "...", "sub": "...", "email": "billy@example.org", "name": "..."}
>>> mapper.map_identity(gair)
'billy'
```

For more serious library usage, implements may want to look at
`globus_identity_mapping.loader.load_mappers`

# Development

The high level bits:

- uses Poetry (`pyproject.toml`)
- uses tox
  - `tox` - enough to run all tests
  - `tox -e mypy` to run mypy
- Reminder to install `pre-commit` at your first checkout: `pre-commit --install`
