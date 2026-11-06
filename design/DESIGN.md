# MealFlow — design plan

## Subject, people, core action, moment
- **Subject:** volunteer community meal delivery dispatch for a fictional Riverside program and 20 older-adult stops.
- **Who uses it:** a dispatcher coordinating volunteer availability and making sure every open stop has a named owner.
- **Core action:** close a delivery safely, or react to a cancellation by reassigning its remaining stops.
- **Moment of use:** on a phone during a live delivery shift, checking a stop one-handed and correcting disruptions quickly.

## Three visual directions
1. **Midnight dispatch board (chosen):** near-black navy, electric green/cobalt/amber, compact SF-style operational typography, dense route cards and clear state badges matching the user's supplied reference screens.
2. **Community field notebook:** warm paper white, ink-blue headings, small route map motifs, editorial serif accents and spacious volunteer profiles.
3. **Civic command center:** graphite canvas, teal and high-visibility orange, mono timestamps and a split-pane control-room dashboard.

Chosen because the user explicitly selected four coherent dark dispatch-screen references. The notebook loses on direct visual mismatch; the split command center loses because its dense split-pane layout is less suited to a phone. Plan check: this is distinct from a generic settings/card layout because its content hierarchy is a live route: completion summary, next stop, voice update, then ordered stops.

## Palette and tokens
- Midnight navy `#050D1A` → app background.
- Route-card navy `#08182A` → surfaces/cards.
- Bright meal-delivery green `#18DE83` → accent/success/completed.
- Route cobalt `#168BFF` → in-progress / voice accent.
- Alert amber `#FFB51B` → delayed / warning.
- Cool slate `#8093B2` → secondary/muted text and open state.
Light theme is intentionally not used: the app keeps its dark reference appearance in every device setting.

## Type and imagery
Compact, crisp platform sans typography; large counts and concise resident names; small but legible secondary route/address lines. Screens use the supplied reference art and no stock photography. Mascot is a blue/cyan community bird holding a green heart/meal symbol, used sparingly as the header identity.

## Shell
```text
┌──────────────────────────┐
│ Status bar               │
│ Scrollable screen content│
│ (compact, dark dispatch) │
│                          │
├──────────────────────────┤
│ Deliveries Volunteers    │
│ Voice Hub Analytics      │  native 4-tab glass bar
└──────────────────────────┘
```

## Screen sketches
### Deliveries — two first-screen sketches; keep A
```text
A  [Today 16/20 + mascot]       B [20 route cards first]
   [green progress + remaining]    [summary stats grid]
   [4 small status counters]      [route list]
   [NEXT STOP + Navigate]         [Next stop]
   [Voice Update]                 [voice update]
   Today's Stops + status key
   [dense stop 1 … stop 20]
```
A is stronger because it matches the reference's progression from shift overview to immediate next action to complete route list. It keeps the actual resident/stops as the content, not a generic dashboard.

### Volunteers
```text
[Volunteers / shift subtitle]
[Available] [On route] [Unavailable] [Total]
[Featured available volunteer + route]
[Upcoming shift]
[Volunteer stats]
[Team roster: availability + stops]
```
### Voice Hub
```text
[Voice Hub / shift subtitle + mascot]
[Start voice update] [short phrase suggestions]
[Last update: transcript + linked stop]
[Recent updates: transcript + result]
```
### Analytics
```text
[Analytics / period selector]
[4 compact KPIs]
[Deliveries by day: stacked bars]
[Average delivery time]
[Delivery windows] [Order types]
[Top areas] [Operational insights]
[Architecture & delivery plan]
```
All screens share the same dark canvas, status language, compact bordered panels and fixed native four-tab bar. Stop/volunteer sheets and voice review retain the same typography, compact controls and navy/green/blue/amber tokens.

## Signature moment
When a dispatcher confirms a delivered stop, its green completion ring draws closed over the stop's number, the completed count updates, and a success haptic fires. Triggered by tapping “Mark delivered” in a stop's detail panel. The moment is short, nonblocking, and only used on delivery closure.

## Identity
MealFlow is unmistakable as a shift-ready meal route board because its bright completed ring and explicitly owned “Next Stop” sit above a dense, resident-first route, with voice updates one tap away.

## Cloud implementation boundary
This prototype runs on device with persistent fictional seed records. No speech AI, Google Cloud service or NVIDIA inference is claimed to be connected. A practical future version would use Newly Backend as the supported app backend, Google Cloud services for authenticated event processing and aggregate operations reporting, and an NVIDIA inference endpoint for speech transcription/intent suggestions, with dispatcher confirmation before any status or assignment changes. See `.newly/brief.md` for security, rollout, resource, risk and timeline details.
