Catalog maintenance
===================

Run `python deduplicate_catalogs.py` after generating catalog files. The existing
builders and weekly workflow already call this finalization step.

The finalizer applies `catalog_policy.json` before assigning one browse owner to
each exact URL/torrent source group. Exclusions propagate across aliases and
remove browse/search results without deleting metadata or stream records.
Phrase fingerprints use normalized word sequences; they are matching data, not
encryption or a security boundary. They match metadata, not the contents of videos.

The additional collections contain existing record IDs only. Known portrait
sources take precedence over general categories. Archive references have their
own category and may point to collection pages rather than directly playable files.

Resolution and aspect ratios come from source labels. They have not been measured
from playback. GPU scaling does not establish native 4K. Static stream URLs can
expire; this addon does not provide a per-click authenticated link resolver.
An available manifest does not prove that individual videos play.

Checks: `python -m unittest test_deduplicate_catalogs -v`.
