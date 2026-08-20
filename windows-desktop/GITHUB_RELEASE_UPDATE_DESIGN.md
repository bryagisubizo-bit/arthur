# GitHub Release Update Design

Arthur should query the designated repository’s **latest published GitHub Release** metadata first, not download an installer merely to check for updates. The GitHub Releases REST endpoint supports latest-release retrieval and can be used without authentication for public repositories. A private repository needs a scoped credential stored only in the Windows Credential Manager.

For limited internet, Arthur should retain the release ETag and make a conditional request. GitHub documents that a `304 Not Modified` conditional response does not count against the primary REST API rate limit. The app should use a user-selected interval, skip checks on a metered connection when configured, and display a small available-update notice rather than fetching release assets.

Before an update asset is downloaded, Arthur should require the user to approve the exact version, asset name, size, and release source. After the download, the app should validate the GitHub asset’s published SHA-256 digest when present. It must never execute an update automatically, mutate source code from a repository branch, or accept an unverified asset.

## Sources

1. GitHub Docs, “REST API endpoints for releases and release assets”: <https://docs.github.com/en/rest/releases>.
2. GitHub Docs, “REST API endpoints for releases”: <https://docs.github.com/en/rest/releases/releases>.
3. GitHub Docs, “Best practices for using the REST API”: <https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api>.
4. GitHub Docs, “Rate limits for the REST API”: <https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api>.
5. GitHub Changelog, “Releases now expose digests for release assets”: <https://github.blog/changelog/2025-06-03-releases-now-expose-digests-for-release-assets/>.
