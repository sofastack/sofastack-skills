# SOFAStack Community Review Repo Policy

## V1 Target Repositories

Prioritize these repositories for the first rollout:

1. `sofastack/sofa-rpc`
2. `sofastack/sofa-jraft`
3. `sofastack/sofa-boot`
4. `sofastack/sofa-bolt`
5. `sofastack/sofa-registry`
6. `sofastack/sofa-tracer`
7. `sofastack/sofa-ark`

Skip archived repositories.
Ignore private repositories unless current credentials can access them and the current run explicitly opts in.

## Repo-specific Maintainers

Use these sets when evaluating `has_newer_maintainer_activity` and when deciding whether a thread is still waiting on maintainers.
Always include `nobodyiam` as a maintainer.

### sofastack/sofa-rpc
- `nobodyiam`
- `EvenLjj`
- `leizhiyuan`
- `ujjboy`
- `OrezzerO`
- `Lo1nt`
- `JervyShi`
- `zonghaishang`

### sofastack/sofa-jraft
- `nobodyiam`
- `fengjiachun`
- `killme2008`
- `horizonzy`
- `shihuili1218`
- `zongtanghu`

### sofastack/sofa-boot
- `nobodyiam`
- `HzjNeverStop`
- `QilongZhang`
- `alaneuler`
- `CrazyHZM`
- `caojie09`
- `guanchao-yang`
- `glmapper`
- `leizhiyuan`

### sofastack/sofa-bolt
- `nobodyiam`
- `xmtsui`
- `dbl-x`
- `chuailiwu`
- `funky-eyes`

### sofastack/sofa-registry
- `nobodyiam`
- `dzdx`
- `nocvalight`
- `Synex-wh`
- `atellwu`
- `huanglongchao`
- `hui-cha`

### sofastack/sofa-tracer
- `nobodyiam`
- `guanchao-yang`
- `glmapper`
- `QilongZhang`
- `xzchaoo`
- `ZijieSong`

### sofastack/sofa-ark
- `nobodyiam`
- `lvjing2`
- `QilongZhang`
- `glmapper`
- `gaosaroma`
- `lylingzhen`
- `yuanyuancin`
- `straybirdzls`

## Automation Accounts to Ignore or De-prioritize

Treat these as automation noise unless a human explicitly asks to review them:

- `stale`
- `stale[bot]`
- `mergify`
- `mergify[bot]`
- `dependabot`
- `dependabot[bot]`
- `app/dependabot`
- `copilot`
- `app/copilot-swe-agent`
- `copilot-pull-request-reviewer`
- `coderabbitai`
- `codecov`
- `sofastack-cla`
- `sofastack-bot`

## Output Policy

- Use compact Chinese maintainer summaries for Jason.
- Keep the sections `Auto-sent`, `Needs review`, and `Skipped/Error`.
- If a run finds no actionable new work, return exactly `HEARTBEAT_OK`.
