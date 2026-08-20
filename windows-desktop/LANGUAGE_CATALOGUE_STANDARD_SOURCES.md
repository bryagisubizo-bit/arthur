# All-Language Catalogue Standard Sources

Arthur’s all-language catalogue uses ISO 639-3 identifiers as its standard code backbone, while user-facing locale tags may need Unicode CLDR/BCP 47 canonicalisation and script or territory subtags.

## ISO 639-3

The official ISO 639-3 download page provides the complete code set, language names index, macrolanguage mappings, and deprecated-code mappings. Its reference names are identifiers for the standard and are not necessarily the preferred names in an application. Arthur therefore preserves an endonym or community-preferred label separately when it is available and attributed.

The terms permit incorporation into software with attribution, but do not permit Arthur to redistribute the official code table. The Windows application therefore treats the full catalogue as a user-approved import source, not a bundled redistribution of the official table.

Source: [ISO 639-3 Downloads](https://iso639-3.sil.org/code_tables/download_tables)

## Unicode CLDR / BCP 47

Unicode CLDR explains that language and locale identifiers use BCP 47-style tags, may need script or territory subtags, and should be verified against the relevant registries. Arthur keeps an ISO 639-3 code as catalogue metadata and stores a locale tag only where the user or an approved language pack supplies a verified tag.

Source: [Unicode CLDR: Picking the Right Language Identifier](https://cldr.unicode.org/index/cldr-spec/picking-the-right-language-code)
