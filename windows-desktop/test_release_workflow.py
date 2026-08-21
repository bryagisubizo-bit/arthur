from pathlib import Path


def main() -> None:
    workflow = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "release-windows.yml"
    text = workflow.read_text(encoding="utf-8")
    assert 'tags:\n      - "v*"' in text
    assert "release_version:" in text
    assert "Semantic version to release" in text
    assert "Release version must use semantic versioning" in text
    assert "--target \"${{ github.sha }}\"" in text
    assert "gh release create" in text
    print("release workflow checks passed")


if __name__ == "__main__":
    main()
