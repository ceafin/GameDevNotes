# Home Infrastructure Architecture

## Hardware Role Assignment

| Device              | Role                                                                                                                                                                                                              |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **UDM Base**        | Gateway, firewall, VLAN routing, WiFi AP, UniFi controller                                                                                                                                                        |
| **USW-Lite-16-PoE** | Primary switch trunk — carries all VLANs to Proxmox & NAS                                                                                                                                                         |
| **NETGEAR GS108E**  | Secondary switch for a second room/rack. **Note:** if using the direct `eth2` NIC-to-NIC storage link (recommended), do not use this switch as storage infrastructure — the two approaches are mutually exclusive |
| **Qotom Q750G5**    | Primary compute (Proxmox) — runs all services as VMs/LXC containers                                                                                                                                               |
| **Synology DS418**  | Canonical storage for all personal media (photos, movies/TV, ebooks, music) plus backups, Git LFS, and service data. NFS-served to Proxmox. Avoid running containers on its ARM CPU                               |
| **Digital Ocean**   | On-demand CPU-burst workloads (Godot builds); also Zulip if RAM-constrained on-prem. PeerTube and Immich are no longer cloud-hosted                                                                              |

## Network Design (VLANs)

### Access Philosophy

**LAN-first, Tailscale for remote.** Every service — whether hosted on-prem or on Digital Ocean — must be reachable by all devices on the local network via a single on-prem Caddy gateway. Laptops, phones, Chromecasts, and Kobos access everything the same way: by hostname, resolved to the on-prem Caddy IP on VLAN 10.

- **On-prem services** (Forgejo, Jellyfin, Immich, Authentik, etc.) → Caddy proxies directly within VLAN 10
- **DO-hosted services** (Godot build server) → only spun up on-demand; no persistent proxy route needed
- **Remote access** (laptops/phones away from home) → Tailscale-connected devices reach the same Caddy instance via the subnet router advertising `10.0.10.0/24`, so the same hostnames and URLs work everywhere
- **LAN-only devices** (Chromecasts, Kobos, smart home) → cannot run Tailscale; they work on-prem only, which is fine since they have no use case off-network

This makes Caddy the **single point of entry for all services**, on-prem and cloud alike. Clients never need to know where a service physically runs.

### VLAN Layout

Use the UDM's VLAN capability and tag ports on both managed switches:

|VLAN|Subnet|Purpose|
|---|---|---|
|**1** (default)|`192.168.1.0/24`|Management — UDM, switches, Proxmox host, Synology management|
|**10**|`10.0.10.0/24`|Services — all self-hosted service VMs/containers|
|**20**|`10.0.20.0/24`|Trusted clients — laptops, phones, Kobos|
|**30**|`10.0.30.0/24`|IoT — Chromecasts, smart home (isolated, no initiation toward other VLANs)|
|**40**|`10.0.40.0/24`|DMZ — anything with ports exposed to the internet|

**Firewall rules on UDM:**

- IoT (VLAN 30) → blocked from initiating connections to most VLANs. **Exception:** allow IoT → Caddy IP on VLAN 10 (specific IP + ports 80/443 only). This is required for Chromecasts to stream from Jellyfin and any other service proxied through Caddy. mDNS discovery still requires the UDM's built-in mDNS repeater enabled in UniFi Network settings
- Trusted (VLAN 20) → can reach Services (VLAN 10) and IoT (VLAN 30)
- Services (VLAN 10) → **blocked** from reaching VLAN 1 (management). NFS access bypasses VLAN routing entirely via the dedicated `eth2` link — no cross-VLAN rule is needed or wanted. Allowing VLAN 10 → VLAN 1 would expose the UDM, managed switches, and Proxmox host management interface to any compromised service container
- DMZ (VLAN 40) → tightly restricted, only specific ports forwarded inbound. **Note:** Caddy lives in VLAN 10 (Services), not VLAN 40, because it is trusted infrastructure. VLAN 40 is reserved for future raw-port-forwarded services that bypass the reverse proxy (e.g., game servers, SIP/VOIP, TURN/STUN). No services in this current plan populate VLAN 40.

### 5-NIC Qotom Strategy

You have a luxury here — dedicate NICs by role:

|NIC|Use|
|---|---|
|`eth0`|Proxmox management (VLAN 1, untagged)|
|`eth1`|VLAN trunk to USW-Lite-16-PoE (carries VLANs 10 and 40 as tagged) — all VM/container traffic. Only include VLAN 20 here if you explicitly need a VM bridged to the trusted-client network; omit it otherwise|
|`eth2`|Direct link to Synology NAS for storage (dedicated NFS/iSCSI, no switch hop, own subnet `10.0.99.0/28`)|
|`eth3`|Optional: dedicated WireGuard interface or second uplink. **Note:** Tailscale does not need a dedicated physical NIC — it creates a virtual `tailscale0` tunnel interface in software. The Tailscale subnet router LXC simply attaches to an existing bridge (vmbr0 or vmbr1)|
|`eth4`|Spare / future use|

The **direct NIC-to-NIC link** between Proxmox and the Synology for storage traffic is the single biggest performance win you can get. It avoids switch contention and gives you a dedicated 1Gbps path for NFS.
Create a `vmbr2` bridge on Proxmox bound to `eth2`. Any VM or LXC that needs direct NFS access (the Docker VM for Forgejo/Authentik, the Jellyfin LXC, etc.) should be given a **second vNIC** attached to `vmbr2` with a static IP in `10.0.99.0/28` (14 usable addresses — enough for the Synology, the Proxmox host, and all current and future NFS-consuming VMs/LXCs). Alternatively, mount NFS at the Proxmox host level and bind-mount paths into containers — but the second-vNIC approach is cleaner and more portable.
## Proxmox Architecture

Create a **single Docker-hosting VM** (or an LXC running Docker) rather than one VM per service. This is far more RAM-efficient on a J4125 system.

### Why this layout

- **One Docker VM** keeps overhead low. The J4125 officially supports up to 8 GB RAM — every additional VM costs ~512 MB+ in overhead.
- **Zulip in its own LXC** because its stack is complex and benefits from isolation. Use their official install script in a Debian LXC. **RocketChat is not used** — it overlaps entirely with Zulip and brings MongoDB as a dependency (~1–2 GB RAM), which is too costly on an 8 GB system.
- **Jellyfin in its own LXC** because it requires `/dev/dri` GPU passthrough for Intel Quick Sync (VAAPI) hardware transcoding. A privileged LXC with the device bind-mounted is far simpler than full PCIe passthrough into the Docker VM. The J4125's Intel UHD 600 comfortably handles 1–2 simultaneous 1080p transcodes.
- **Caddy over Traefik/nginx** because it handles automatic HTTPS (Let's Encrypt / ZeroSSL) with near-zero config and has first-class Tailscale HTTPS cert integration.
- **Anubis** sits as a proof-of-work challenge layer in front of individual services to block bots. Chain it: `Internet → port forward → Caddy → Anubis → service`. Caddy terminates TLS and routes per hostname; Anubis wraps each upstream service behind it.

### Auth Stack: LLDAP + Authentik

- **LLDAP** is your user directory — manage users/groups here.
- **Authentik** consumes LLDAP as its LDAP source, then exposes OAuth2/OIDC/SAML to all your apps.
- Authentik also integrates with Caddy via forward-auth for protecting arbitrary web sites.
### Single Sign-On (SSO)

**One login, everywhere.** Authentik is the sole identity provider. A user logs in once at `auth.home.lab` and every other service recognizes the active session automatically — no repeated login prompts.

**How it works:** all services live under a shared domain (`*.home.lab`). When a user hits any service, either the app redirects to Authentik via OIDC or Caddy's forward-auth checks with Authentik before proxying. If Authentik already has an active session (browser cookie from the first login), it silently grants access and redirects back — the user never sees a second login screen.

**SSO method per service:**

|Service|SSO Method|Notes|
|---|---|---|
|Forgejo|Native OIDC|Built-in OpenID Connect support; configure Authentik as the OIDC provider|
|Zulip|Native OIDC/SAML|Supports OpenID Connect natively|
|Immich|Native OAuth2/OIDC|Supports external OAuth2 providers; runs on-prem in the Docker VM|
|Jellyfin|OIDC via SSO plugin|Install `jellyfin-plugin-sso` — adds OpenID Connect support. Pairs user identities with Jellyfin's internal accounts on first login|
|Static web sites|Caddy forward-auth|Caddy checks with Authentik before serving; no app-level auth needed. Fully transparent SSO|
|Grafana (future)|Native OIDC|If ever added — built-in OAuth2/OIDC support|

**What forward-auth covers:** any service that doesn't natively support OIDC can still participate in SSO via Caddy's `forward_auth` directive. Caddy sends a subrequest to Authentik before proxying; Authentik checks the session cookie and either grants access (transparent) or redirects to the login page. Authentik passes identity headers (`X-Authentik-Username`, `X-Authentik-Email`, `X-Authentik-Groups`) downstream, so the proxied service can identify the user if it supports trusted-header auth.

**LAN-only devices (Chromecasts, Kobos):** these cannot participate in browser-based SSO. Jellyfin clients on Chromecasts authenticate via Jellyfin's device auth flow (entered once on initial setup). Kobos pulling ebooks don't need authentication if the OPDS/Calibre-web endpoint is restricted to VLAN 20 at the firewall level instead.### Offline Login for Laptops (Linux/macOS)

OS-level login uses **LDAP via SSSD** (Linux) or **NoMAD/Jamf Connect** (macOS), not OIDC — because OIDC has no offline mode.

- **Linux laptops:** configure SSSD with `ldap_provider = ldap` pointing at LLDAP (via Authentik's LDAP outpost or directly). SSSD caches credentials locally by default (`cache_credentials = True`). Set `offline_credentials_expiration` to 30+ days.
- **macOS laptops:** use an LDAP-aware login tool (e.g., NoMAD Login or Jamf Connect) that caches credentials locally for offline use. Native macOS directory binding to LDAP also supports cached login.
- **First login must happen on-prem** (or anywhere Authentik/LLDAP is reachable via Tailscale) so the credential cache is populated.
- After that, the offline flow is: cached login → desktop → Tailscale starts (it runs as a systemd service on Linux / LaunchDaemon on macOS, auto-connecting at boot) → all services reachable.
- **Password changes while offline** won't propagate until the laptop reconnects; SSSD handles this gracefully by accepting both old and new passwords during the transition.
- **No Windows or Microsoft products exist in this environment.** All clients are Linux, BSD, or macOS.
## What Goes Where: On-Prem vs. Cloud

|Service|Where|Why|
|---|---|---|
|LLDAP|Proxmox|Tiny, must be local, <50MB RAM|
|Authentik|Proxmox|Core infra, low latency to all services|
|Forgejo|Proxmox|Light, repos stored on Synology NFS|
|Jellyfin|Proxmox|Media server in its own LXC with iGPU passthrough (`/dev/dri`) for VAAPI hardware transcoding. Media libraries stored on Synology NFS: **Movies/TV**, **Music**, and **Personal Videos** (home videos, recordings, etc.) as separate Jellyfin libraries. The J4125's Intel UHD 600 handles 1–2 simultaneous 1080p transcodes; direct-play clients (e.g., on LAN) need zero CPU. **Replaces PeerTube** — there is no need for a separate video platform when Jellyfin serves personal videos natively|
|Immich|Proxmox|Photo management in the Docker VM via Docker Compose. **ML worker disabled** — the J4125 cannot handle facial recognition/CLIP inference, but the full photo browsing, albums, timeline, and upload experience is preserved. Photos read directly from Synology NFS (no cloud sync needed). ML can be re-enabled later if hardware is upgraded. ~1–1.5 GB RAM|
|Anubis|Proxmox|Wraps individual services behind Caddy; Caddy routes per hostname to Anubis, then to service|
|Caddy|Proxmox|**Unified reverse proxy for ALL services.** All services are now on-prem; Caddy proxies directly within VLAN 10. From any client's perspective, every service is just a hostname pointing at Caddy|
|Web sites|Proxmox|Static sites via Caddy, trivial resource use|
|Zulip|Proxmox or DO|Fine for a small team (<50 users) on-prem if 16 GB RAM is confirmed. At 8 GB, **move Zulip to DO** (~$12–24/mo) to make room for Jellyfin and the rest of the stack|
|**PeerTube**|**Removed**|Replaced by a dedicated Jellyfin "Personal Videos" library. No separate platform needed for serving personal video files|
|**Immich**|**Proxmox (moved on-prem)**|Runs in the Docker VM via Docker Compose with ML worker disabled. Photos served directly from Synology NFS — no DO Spaces, no rclone sync. Dramatically simpler than the previous cloud-hosted approach|
|**Godot build server**|**Digital Ocean**|CPU-burst workload. Spin up on-demand via API and destroy when done — the only remaining DO service|
|Tailscale subnet router|Proxmox|Lightweight LXC that advertises `10.0.10.0/24` over Tailscale, enabling remote access to services without port-forwarding. **Not** an exit node (which would route all remote internet traffic through your home connection — a different, unrelated feature)|

## Digital Ocean Monthly Cost Estimates

With Immich and PeerTube moved on-prem, DO is now used **only for the Godot build server** (on-demand).

|Service|Droplet|Storage|Est. Monthly|
|---|---|---|---|
|Godot build server|On-demand only — spin up per build, destroy when done|None|~$5–15/mo usage-billed|
|Zulip (if RAM-constrained)|$12–24/mo shared/dedicated|None|~$12–24/mo|
|**Total**|–|–|**~$5–39/mo**|

This is a significant cost reduction from the previous ~$63–107/mo estimate with PeerTube and Immich on DO.

## Tailscale Integration

**Tailscale is the remote-access layer, not the primary access path.** On-prem, all traffic stays on the LAN and never touches Tailscale.

- **Subnet router LXC** on Proxmox advertises `10.0.10.0/24` (services VLAN). When a laptop or phone leaves the home network, it reaches the same Caddy instance and the same service hostnames via this advertised route — zero URL changes, zero reconfiguration.
- **DO droplets** (Godot build server, and Zulip if offloaded) join the Tailnet when active. They bind only to their Tailscale interface (`100.x.y.z`), never a public IP.
- **Split DNS** is required to make this seamless:
  - **On-prem (UDM DNS):** `*.home.lab` (or your chosen domain) resolves to Caddy's VLAN 10 IP (e.g., `10.0.10.10`). Configure this in the UDM's DNS settings or run a lightweight DNS in the Docker VM (e.g., CoreDNS, dnsmasq).
  - **Remote (Tailscale MagicDNS):** override the same hostnames to resolve to Caddy's VLAN 10 IP. Since the subnet router advertises `10.0.10.0/24`, remote clients route to Caddy the same way LAN clients do.
  - This means the **same URL works everywhere** — `https://jellyfin.home.lab` resolves to `10.0.10.10` both on-prem and over Tailscale.
- **Tailscale Funnel** is available if you ever want a specific on-prem service (e.g., Forgejo, a static site) reachable from the public internet without opening firewall ports. No current services require this.
- **Devices without Tailscale** (Chromecasts, Kobos, IoT) are LAN-only by design. They reach everything through Caddy on VLAN 10 and have no off-network use case.

## Synology DS418 Role

The DS418 (ARM RTD1296) is **storage only** and the **canonical archive for all personal media**:

- NFS export mounted by Proxmox over the dedicated `eth2` link (`10.0.99.0/28`)
- **Photos/images** — served directly to Immich via NFS mount in the Docker VM. Immich reads the existing photo library in-place; new uploads via Immich's UI are written to the same NFS path. No cloud sync needed
- **Movies, TV, music** — served directly to Jellyfin via NFS (separate Jellyfin libraries)
- **Personal videos** (home videos, recordings, non-TV content) — served to Jellyfin via NFS as a dedicated "Personal Videos" library, separate from Movies/TV. **Replaces PeerTube**
- **Ebooks** — stored here; available for a future Calibre-web or OPDS server if desired (Kobos on VLAN 20 can pull from it)
- **Service data** — Forgejo repos, Zulip uploads, backups
- Use **NFSv4** with a configured lock daemon; NFSv3 advisory locking has known issues with concurrent git operations and can cause Forgejo corruption under load
- Run **Hyper Backup** to back up critical data (repos, service configs, ebook metadata, Immich database exports) to a DO Spaces bucket (S3)
- Do NOT run Docker containers on it — the ARM CPU and limited RAM make this painful

## Critical Bottleneck: RAM

**Check how much RAM your Q750G5 has.** The J4125 officially supports up to 8 GB DDR4 per Intel's spec. Some boards have been reported to POST with a 16 GB SO-DIMM, but this is unofficial and stability is not guaranteed — do not count on 16 GB as a reliable upgrade path. Your service stack needs roughly:

|Service|RAM|
|---|---|
|Proxmox host overhead|~1 GB|
|Docker VM (base)|~512 MB|
|Caddy + Anubis|~128 MB|
|Authentik (server + worker + Postgres + Redis)|~2–3 GB|
|LLDAP|~50 MB|
|Forgejo|~256 MB|
|Immich (server + Postgres + Redis, ML disabled)|~1–1.5 GB|
|Jellyfin (LXC)|~512 MB–1 GB|
|Zulip (LXC)|~2–3 GB|
|**Total**|**~8–10.5 GB**|

At 8 GB, this stack **does not fit** with Zulip on-prem. Move Zulip to DO (~$12–24/mo droplet), which frees ~2–3 GB and brings the on-prem total to ~6–7.5 GB — tight but workable with Immich, Jellyfin, and everything else. The 16 GB upgrade is desirable but uncertain on the J4125 (see note above); confirm SO-DIMM compatibility with your specific board before purchasing. At 16 GB, everything including Zulip fits comfortably.

## Summary: Order of Implementation

1. **Network first** — set up VLANs on UDM + switches, wire the dedicated Proxmox↔Synology NFS link
2. **Proxmox base** — configure NIC bridges, NFS mount, create the Docker VM
3. **Caddy + Anubis** — get reverse proxy working with a test site
4. **LLDAP + Authentik** — identity stack before anything else
5. **Forgejo** — connected to Authentik via OIDC
6. **Jellyfin** — in its own LXC with `/dev/dri` passthrough; mount Synology media libraries (Movies, TV, Music, Personal Videos) via NFS on `vmbr2`; connect to Authentik via OIDC SSO plugin
7. **Immich** — Docker Compose in the Docker VM; mount Synology photos directory via NFS on `vmbr2`; ML worker disabled; connect to Authentik via OAuth2/OIDC
8. **Zulip** — in its own LXC on-prem if 16 GB confirmed, otherwise deploy to DO
9. **Godot build server** — on Digital Ocean, joined to Tailnet, spun up on-demand
10. **Harden** — firewall rules, fail2ban, automatic updates, Hyper Backup to DO Spaces