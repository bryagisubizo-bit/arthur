# Lovable App-Development Capability — Verified Integration Boundary

Arthur may present Lovable as a **developer-owned app-development capability**, not as a general-purpose data source or an automatically connected API. The user must explicitly approve the target Lovable account and workspace before any real project operation is requested.

## Selected connection model

| Item | Selected handling in Arthur |
|---|---|
| Primary interface | Lovable’s official MCP server at `https://mcp.lovable.dev` |
| Authentication | User-completed OAuth in a supported MCP client; **no API-key field is shown for MCP** |
| Capability | Create, inspect, iterate on, and optionally deploy Lovable projects after explicit project/workspace selection and approval |
| Preview test | Reports that OAuth and protected server/desktop validation are required; it does not contact Lovable or expose credentials |
| Publish boundary | Project creation, code changes, connector changes, and deployment remain approval-gated actions |

> Lovable documents its MCP server as the route that allows an external AI client to manage Lovable projects, and states that OAuth—not API-key authentication—is the supported connection method.[1]

## What Arthur will not claim

Arthur will not claim that a Lovable account, workspace, project, or token is connected unless a protected desktop or server adapter has completed the OAuth flow and recorded an approved connection status. The browser preview therefore labels the room **Add API / OAuth required** and keeps its test result non-networked.

Lovable’s separate **Build with URL** feature can generate or share an app-creation link. It is not treated as the credential-bearing control route for Arthur’s desktop assistant.[2]

## References

[1]: https://docs.lovable.dev/integrations/lovable-mcp-server "Lovable MCP server documentation"
[2]: https://docs.lovable.dev/integrations/lovable-api "Lovable API documentation"
[3]: https://docs.lovable.dev/integrations/introduction "Lovable integrations documentation"
