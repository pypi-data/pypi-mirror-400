# ATP-Protocol

ATP Protocol is a **payment-gated agent execution API** that makes **agent-to-agent payments** and “pay to unlock results” easy on **Solana**, with a simple client integration (two endpoints + a Solana payment).

At a high level:

- An agent (or any client) requests work from another agent via the ATP Gateway.
- The Gateway executes the upstream agent immediately, but **returns a 402 challenge** instead of the result.
- The requester pays **once** to the agent treasury (in **SOL** or **USDC**).
- After settlement, the Gateway releases the stored agent output.

The ATP Gateway exposes:

- `POST /v1/agent/trade`: execute + return payment challenge (402)
- `POST /v1/agent/settle`: facilitator signs+submits payment (using provided private key) + releases output
- optional helper endpoints for token price/payment info

---

## One simple end-to-end example (trade → settle)

Run the server, then run:

```bash
export ATP_BASE_URL="http://localhost:8000"
export ATP_USER_WALLET="<YOUR_SOLANA_PUBKEY>"
export ATP_PRIVATE_KEY="<YOUR_PRIVATE_KEY_STRING>"

# Safety switch: settlement will broadcast a real SOL transaction
export ATP_ALLOW_SPEND="true"

python full_flow_example.py
```

Notes:
- The first call (`/v1/agent/trade`) returns **HTTP 402** with a `job_id` and the payment challenge JSON.
- The second call (`/v1/agent/settle`) signs+sends the SOL payment in-memory and returns **HTTP 200** with `agent_output`.

Server-side pricing (optional):
- Set `INPUT_COST_PER_MILLION_USD` and/or `OUTPUT_COST_PER_MILLION_USD` on the server to compute `usd_cost` from `usage` token counts.
- If not set (or if token counts are missing), the gateway falls back to upstream `usage.total_cost` (and then a small default).

---

## Conceptual purpose

ATP exists to solve a common agentic workflow problem:

- Agents can call other agents (“agent tools”, “specialist agents”, “market-data agents”), but **payments and settlement** are usually ad-hoc.
- ATP standardizes **a simple handshake**: *execute → challenge → pay → settle → release*.
- Because the settlement happens on Solana, it’s **cheap**, **fast**, and can be done by **another agent** programmatically (no human-in-the-loop required).

Key design goals:

- **Agent-to-agent friendly**: the “client” can be another agent, a bot, or a backend service.
- **Simple integration**: clients can settle by providing a private key string for a single request (used in-memory only).
- **Token flexibility**: support SOL today, and USDC as a stable-priced option.

---

## Core actors

- **Requester (Agent A)**: wants work done (submits the task, later pays and settles).
- **ATP Gateway**: runs the upstream agent, produces the payment challenge, holds the result temporarily.
- **Upstream Agent Service (Swarms API)**: executes the requested agent workload.
- **Solana**: settlement rail (payment transaction + signature).
- **Facilitator**: signs+submits the payment transaction during settlement.
- **Agent Treasury**: receives the payment (minus the fee split logic described below).
- **Swarms Treasury**: receives the **5% settlement fee**.
- **Temporary lockbox**: the gateway holds the output until paid (expires after a TTL).

---

## How it works (step-by-step)

### 1) Request a trade (create challenge)

The requester calls:

- `POST /v1/agent/trade`

with:

- `agent_config`: full agent spec (see `atp/schemas.py:AgentSpec`)
- `task`: what to do
- `user_wallet`: payer public key (used during verification)
- `payment_token`: `SOL` or `USDC`
- optional `history` / `img` / `imgs`

### 2) Gateway executes the agent immediately

The Gateway forwards the request to the upstream agent service (`SWARMS_API_URL`) and waits for completion.

### 3) Gateway computes the price + fee split

The Gateway:

- reads the USD cost from upstream usage (`usage.total_cost`, with a fallback),
- fetches token/USD price (SOL via CoinGecko, USDC treated as $1),
- computes the **total payment** and the **5% settlement fee**.

Important: the fee is **taken from the total** (not added on top):
\[
\text{total} = \frac{\text{usd\_cost}}{\text{token\_price}}
\quad
\text{fee} = 0.05 \cdot \text{total}
\quad
\text{agent\_receives} = \text{total} - \text{fee}
\]

### 4) Gateway stores the result (locked) with a TTL

The agent output is held in a temporary lockbox under a generated `job_id`.

If the requester never pays, the job expires automatically (default TTL: 10 minutes).

### 5) Gateway returns a 402 Payment Required challenge

Instead of returning the agent output, the Gateway returns **HTTP 402** with a JSON payload containing:

- `job_id`
- `recipient` (the agent treasury pubkey)
- amount to pay (in lamports or USDC micro-units)
- a memo format like `ATP:{job_id}`
- a fee breakdown (5% to Swarms treasury)
- TTL info

### 6) Requester pays on Solana

The requester provides a private key string during settlement; the gateway signs+sends the SOL payment transaction in-memory.

### 7) Settle to unlock

The requester calls:

- `POST /v1/agent/settle`

with:

- `job_id`
- `private_key`

### 8) Gateway verifies and releases the output

The Gateway:

- looks up the pending job by `job_id`,
- signs+sends the on-chain payment transaction and verifies it succeeded,
- releases the output exactly once (prevents double-settlement),
- returns the stored `agent_output` and settlement details.

---

## Diagrams

### Architecture overview

```mermaid
flowchart LR
  A["Requester<br/>(Agent A / App / Bot)"] -->|POST /v1/agent/trade| G["ATP Gateway<br/>FastAPI"]
  G -->|Execute task| S["Swarms Agent API<br/>Upstream execution"]
  S -->|Result + usage cost| G

  A -->|POST /v1/agent/settle<br/>(job_id, private_key)| G
  G <-->|Send payment tx| C["Solana<br/>(SOL / USDC)"]
  G -->|Verify signature status| C
  G -->|Unlocked agent output| A

  C --> T1[Agent Treasury]
  C --> T2["Swarms Treasury<br/>(5% fee)"]
```

### End-to-end sequence (challenge → payment → settlement)

```mermaid
sequenceDiagram
  autonumber
  participant A as Requester (Agent A)
  participant G as ATP Gateway
  participant S as Swarms Agent API
  participant C as Solana

  A->>G: POST /v1/agent/trade (agent_config, task, wallet, token)
  G->>S: Execute agent task
  S-->>G: outputs + usage.total_cost
  G->>G: Compute total + 5% fee split<br/>(fetch token price)
  G->>G: Lock result (job_id, ttl)
  G-->>A: 402 Payment Required<br/>(job_id + payment instruction)

  A->>G: POST /v1/agent/settle (job_id, private_key)
  G->>C: Send payment tx (SOL/USDC)<br/>recipient=Agent Treasury
  C-->>G: tx_signature
  G->>G: Load locked job by job_id
  G->>C: Verify tx signature success
  G->>G: Release output once
  G-->>A: 200 OK (agent_output + settlement_details)
```

### Job lifecycle / state machine

```mermaid
stateDiagram-v2
  [*] --> Created: /v1/agent/trade<br/>job_id minted
  Created --> Locked: result locked until paid
  Locked --> Expired: TTL elapses<br/>(no settlement)
  Locked --> Settling: /v1/agent/settle<br/>signed payment submitted
  Settling --> Released: signature verified<br/>output released
  Settling --> Locked: verification failed<br/>job remains until TTL
  Released --> [*]
  Expired --> [*]
```

---

## Client expectations (what you can rely on)

- **Two-call integration**: request work via `/v1/agent/trade`, then unlock via `/v1/agent/settle`.
- **Single payment**: you pay once to the `recipient` address returned by the 402 challenge.
- **Clear fee disclosure**: the 402 includes a breakdown showing the **5% settlement fee** and who receives it.
- **Time-bounded**: each `job_id` expires after `ttl_seconds` if you don't settle in time.

---

## ATP Settlement Middleware

The ATP Settlement Middleware enables **automatic payment processing** for any FastAPI endpoint. Unlike the main ATP Gateway (which uses a 402 challenge), the middleware handles payment **automatically after** your endpoint executes—perfect for APIs that want seamless billing.

### How It Works

The middleware intercepts requests, executes your endpoint, then automatically processes payment:

```mermaid
sequenceDiagram
  autonumber
  participant C as Client
  participant M as Middleware
  participant E as Endpoint
  participant SS as Settlement Service
  participant S as Solana

  C->>M: POST /v1/chat<br/>(x-wallet-private-key header)
  M->>E: Forward request
  E-->>M: Response + usage data
  M->>M: Extract token usage<br/>(auto-detects format)
  M->>SS: Calculate payment<br/>(usage → USD → SOL/USDC)
  SS->>SS: Split payment<br/>(95% recipient, 5% treasury)
  SS->>S: Send payment transaction
  S-->>SS: Transaction signature
  SS-->>M: Settlement details
  M->>M: Add settlement info<br/>to response
  M-->>C: Response + atp_settlement
```

**Step-by-step:**

1. **Client sends request** with wallet private key in header (`x-wallet-private-key`)
2. **Middleware forwards** request to your endpoint
3. **Endpoint executes** and returns response with usage data
4. **Middleware extracts** token counts (supports OpenAI, Anthropic, Google, etc.)
5. **Settlement service calculates** cost: `(input_tokens × input_rate + output_tokens × output_rate) / 1M`
6. **Settlement service splits** payment: 95% to recipient, 5% to Swarms Treasury
7. **Settlement service sends** Solana transaction
8. **Middleware adds** settlement info to response and returns to client

### Quick Start

```python
from fastapi import FastAPI
from atp.middleware import ATPSettlementMiddleware
from atp.schemas import PaymentToken

app = FastAPI()

app.add_middleware(
    ATPSettlementMiddleware,
    allowed_endpoints=["/v1/chat", "/v1/completions"],
    input_cost_per_million_usd=10.0,   # $10 per million input tokens
    output_cost_per_million_usd=30.0,  # $30 per million output tokens
    recipient_pubkey="YourPublicKeyHere",  # Your wallet receives 95%
    payment_token=PaymentToken.SOL,
)
```

**Client request:**
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "x-wallet-private-key: [1,2,3,...]" \
  -d '{"message": "Hello!"}'
```

**Your endpoint:**
```python
@app.post("/v1/chat")
async def chat(request: dict):
    return {
        "output": "Response here",
        "usage": {
            "input_tokens": 150,
            "output_tokens": 50,
        }
    }
```

**Response includes settlement:**
```json
{
  "output": "Response here",
  "usage": {"input_tokens": 150, "output_tokens": 50},
  "atp_settlement": {
    "status": "paid",
    "transaction_signature": "5j7s8K9...",
    "payment": {
      "total_amount_sol": 0.0003,
      "recipient": {"amount_sol": 0.000285},
      "treasury": {"amount_sol": 0.000015}
    }
  }
}
```

### Configuration

| Parameter | Required | Description |
|-----------|----------|-------------|
| `allowed_endpoints` | ✅ | List of paths to apply settlement (e.g., `["/v1/chat"]`) |
| `input_cost_per_million_usd` | ✅ | Cost per million input tokens |
| `output_cost_per_million_usd` | ✅ | Cost per million output tokens |
| `recipient_pubkey` | ✅ | Your Solana wallet (receives 95% of payment) |
| `wallet_private_key_header` | ❌ | Header name for wallet key (default: `x-wallet-private-key`) |
| `payment_token` | ❌ | `PaymentToken.SOL` or `PaymentToken.USDC` (default: SOL) |
| `require_wallet` | ❌ | Require wallet key or skip settlement (default: `True`) |
| `settlement_service_url` | ❌ | Settlement service URL (default: from `ATP_SETTLEMENT_URL` env) |

### Payment Calculation

The middleware uses your configured rates to calculate cost:

```
usd_cost = (input_tokens / 1,000,000 × input_rate) + (output_tokens / 1,000,000 × output_rate)
token_amount = usd_cost / token_price_usd
```

Payment is split automatically:
- **95%** → `recipient_pubkey` (your wallet)
- **5%** → Swarms Treasury (processing fee)

The fee is **deducted from the total** (not added on top).

### Supported Usage Formats

The middleware auto-detects usage from common API formats:

- **OpenAI**: `prompt_tokens`, `completion_tokens`
- **Anthropic**: `input_tokens`, `output_tokens`
- **Google/Gemini**: `promptTokenCount`, `candidatesTokenCount`
- **Generic**: `input_tokens`, `output_tokens`, `total_tokens`
- **Nested**: `usage.*`, `meta.usage`, `statistics.*`

### Middleware vs. Main Protocol

| Feature | Main Gateway | Middleware |
|---------|--------------|------------|
| **Flow** | Two-step: 402 challenge → settle | Automatic: single request |
| **Use Case** | Pay-to-unlock results | Per-request billing |
| **Integration** | Two API calls | One API call |

**Use middleware for:** Automatic billing on every request  
**Use main protocol for:** Explicit payment approval before results
