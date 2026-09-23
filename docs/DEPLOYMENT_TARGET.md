# Worldbook deployment target

Read-only verification on 2026-09-22. No checkout, remotes, branch, GitHub configuration or deployment was changed.

## Verified serving repository and path

**The current production target is `never-nude/worldbook2`, branch `main`, with the atlas at `v2/index.html`.** The restored checkout's `mike-kushman` remotes are not the current serving repositories.

Evidence is stronger than a matching HTML file:

- The [latest deployment record](https://api.github.com/repos/never-nude/worldbook2/deployments?per_page=1) identifies `main` at `bfae443b37e7978b1a11c029c136b8e74d115f01`, environment `github-pages`.
- Its [deployment status](https://api.github.com/repos/never-nude/worldbook2/deployments/6540211746/statuses) is **success**, with `environment_url: https://worldbook.earth/`, at `2026-09-19T11:11:35Z`. [Deployment run](https://github.com/never-nude/worldbook2/actions/runs/35439414776/job/105887548967).
- The [workflow at the deployed revision](https://github.com/never-nude/worldbook2/blob/bfae443b37e7978b1a11c029c136b8e74d115f01/.github/workflows/pages.yml) runs on pushes to `main` or manual dispatch. It uploads the **repository root (`path: .`)** as a Pages artifact and deploys it through the Pages API.
- The deployed revision's [CNAME](https://github.com/never-nude/worldbook2/blob/bfae443b37e7978b1a11c029c136b8e74d115f01/CNAME) contains `worldbook.earth`.
- The deployed [root index](https://github.com/never-nude/worldbook2/blob/bfae443b37e7978b1a11c029c136b8e74d115f01/index.html) is a 441-byte redirect to `/v2/`; the deployed [atlas](https://github.com/never-nude/worldbook2/blob/bfae443b37e7978b1a11c029c136b8e74d115f01/v2/index.html) is a separate file. Both match their respective live responses byte-for-byte.
- DNS corroborates the account: `www.worldbook.earth` CNAME is `never-nude.github.io`. The apex resolves to GitHub Pages IPs, and live responses identify `Server: GitHub.com`. DNS alone was not used to infer the repository.

The production main HEAD is `bfae443b37e7978b1a11c029c136b8e74d115f01` (2026-09-19 11:11:10 UTC, “Add shared Codex instructions and project status (#1)”). The latest commit changes `AGENTS.md` and `STATUS.md`.

## Restored checkout versus remotes

| Repository / role | Current default/main HEAD | Observed Pages state |
| --- | --- | --- |
| `mike-kushman/worldbook-weekly` — local `origin` | `2912389f45b27f32434ddb7e418bdeb1074b2d68` | Repository API reports `has_pages: false`; latest recorded deployment failed, July 28 |
| `mike-kushman/worldbook2` — local `upstream` | `dfb13c6e349ec29342019d2f33896d186d494503` | Repository API reports `has_pages: false`; latest recorded deployment failed, July 7 |
| `never-nude/worldbook2` — serving production | `bfae443b37e7978b1a11c029c136b8e74d115f01` | `has_pages: true`; successful deployment explicitly names `https://worldbook.earth/` |

The working branch is `codex/forensic-trails`, based on `b0dc9c9f4e331d97799a0473f662138981077b6a`. The [origin comparison](https://api.github.com/repos/mike-kushman/worldbook-weekly/compare/b0dc9c9f4e331d97799a0473f662138981077b6a...2912389f45b27f32434ddb7e418bdeb1074b2d68) reports **one commit ahead, zero behind, and no changed files**: the only extra commit is the merge of the statue branch.

Comparing `b0dc9c9` to either `worldbook2` main through GitHub's compare API returned 404. This does not establish an ancestry relationship or a full-tree difference. The important verified content relationship is that **local baseline `index.html` equals production `v2/index.html`**, whereas production root `index.html` is a redirect.

| Content checked | SHA-256 |
| --- | --- |
| Baseline local atlas; deployed `v2/index.html`; live `/v2/` | `1e0bf2fc2e44624bccb9804efd546cb4fd6333cced689450df96548bd3d4a019` |
| Deployed root redirect; live `/` | `8d175923de715d0d3a7b6b4282c78e67d521bbd71a4a9728fc9cd33380787544` |

## Release implications

1. Prepare release integration against the current `never-nude/worldbook2` main and read that repository's current instructions. The restored local remotes should not be treated as production deployment authority.
2. Map the local atlas change to **`v2/index.html`**, preserving the production root redirect and other existing content. New relative reader assets must accompany the atlas under `/v2/` at the paths its references resolve to.
3. Preserve deployed revision `bfae443b37e7978b1a11c029c136b8e74d115f01` as the recorded rollback point and recheck remote HEAD before any release, since this is a dated observation.
4. Check the prepared revision and asset paths before publishing, then verify the resulting deployment status and live `/v2/` behavior.

`gh` is installed but unauthenticated in this restored environment. This audit used read-only public GitHub API calls, raw files pinned to the deployed SHA, DNS, and live HTTP responses. The authenticated Pages settings endpoint was unavailable (404 without authentication), and **write access has not been established**. Successful deployment records and the inspected workflow establish the current target; they do not establish permission to publish from this machine.
