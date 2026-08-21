# Arthur GitHub Release Process

Arthur’s source is stored in the private repository [`bryagisubizo-bit/arthur`](https://github.com/bryagisubizo-bit/arthur). Ordinary pushes save reviewed source; they do **not** automatically publish a Windows installer. This prevents a partially tested change from becoming an update that users may install.

| Action | What happens | When to use it |
|---|---|---|
| Push a normal commit to `main` | Saves source for collaboration and future work. | During implementation. |
| Push a semantic version tag such as `v0.1.2` | Runs the Windows regression suite, builds with PyInstaller and Inno Setup, then publishes the installer as a GitHub release. | After a feature is complete and validated. |
| Start the **Release Arthur for Windows** workflow manually with `0.1.2` | Builds the current chosen commit and creates the matching `v0.1.2` release. | When a deliberate release is needed without creating a tag locally. |

## Safe release checklist

1. Confirm the browser and desktop regression suites pass, and ensure any changed desktop files are synchronized into `windows-desktop/`.
2. Review the source for accidental API keys, personal data, and `.env` files before publishing.
3. Select the next semantic version. Use `vMAJOR.MINOR.PATCH`; for example, `v0.1.2`.
4. Either push that tag or start the release workflow manually. The workflow validates the source before it creates the installer release.
5. Review the generated GitHub release asset and its SHA-256 digest before inviting a user to download it. Arthur’s updater remains manual and asks separately before any download or installer hand-off.

> A GitHub release is an approved installer publication, not a background-update mechanism. New Arthur features should be released only after their consent boundaries and regression checks are complete.
