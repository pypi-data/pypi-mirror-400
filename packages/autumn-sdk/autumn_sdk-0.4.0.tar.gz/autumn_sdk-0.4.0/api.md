# Shared Types

```python
from autumn.types import BaseCustomer, Customer, CustomerData, Entity, EntityData, Plan, PlanFeature
```

# Autumn

Types:

```python
from autumn.types import (
    AttachResponse,
    BillingPortalResponse,
    CancelResponse,
    CheckResponse,
    CheckoutResponse,
    QueryResponse,
    SetupPaymentResponse,
    TrackResponse,
)
```

Methods:

- <code title="post /attach">client.<a href="./src/autumn/_client.py">attach</a>(\*\*<a href="src/autumn/types/client_attach_params.py">params</a>) -> <a href="./src/autumn/types/attach_response.py">AttachResponse</a></code>
- <code title="post /customers/{customer_id}/billing_portal">client.<a href="./src/autumn/_client.py">billing_portal</a>(customer_id, \*\*<a href="src/autumn/types/client_billing_portal_params.py">params</a>) -> <a href="./src/autumn/types/billing_portal_response.py">BillingPortalResponse</a></code>
- <code title="post /cancel">client.<a href="./src/autumn/_client.py">cancel</a>(\*\*<a href="src/autumn/types/client_cancel_params.py">params</a>) -> <a href="./src/autumn/types/cancel_response.py">CancelResponse</a></code>
- <code title="post /check">client.<a href="./src/autumn/_client.py">check</a>(\*\*<a href="src/autumn/types/client_check_params.py">params</a>) -> <a href="./src/autumn/types/check_response.py">CheckResponse</a></code>
- <code title="post /checkout">client.<a href="./src/autumn/_client.py">checkout</a>(\*\*<a href="src/autumn/types/client_checkout_params.py">params</a>) -> <a href="./src/autumn/types/checkout_response.py">CheckoutResponse</a></code>
- <code title="post /query">client.<a href="./src/autumn/_client.py">query</a>(\*\*<a href="src/autumn/types/client_query_params.py">params</a>) -> <a href="./src/autumn/types/query_response.py">QueryResponse</a></code>
- <code title="post /setup_payment">client.<a href="./src/autumn/_client.py">setup_payment</a>(\*\*<a href="src/autumn/types/client_setup_payment_params.py">params</a>) -> <a href="./src/autumn/types/setup_payment_response.py">SetupPaymentResponse</a></code>
- <code title="post /track">client.<a href="./src/autumn/_client.py">track</a>(\*\*<a href="src/autumn/types/client_track_params.py">params</a>) -> <a href="./src/autumn/types/track_response.py">TrackResponse</a></code>

# Customers

Types:

```python
from autumn.types import CustomerListResponse, CustomerDeleteResponse
```

Methods:

- <code title="post /customers">client.customers.<a href="./src/autumn/resources/customers.py">create</a>(\*\*<a href="src/autumn/types/customer_create_params.py">params</a>) -> <a href="./src/autumn/types/shared/customer.py">Customer</a></code>
- <code title="post /customers/{customer_id}">client.customers.<a href="./src/autumn/resources/customers.py">update</a>(customer_id, \*\*<a href="src/autumn/types/customer_update_params.py">params</a>) -> <a href="./src/autumn/types/shared/customer.py">Customer</a></code>
- <code title="post /customers/list">client.customers.<a href="./src/autumn/resources/customers.py">list</a>(\*\*<a href="src/autumn/types/customer_list_params.py">params</a>) -> <a href="./src/autumn/types/customer_list_response.py">CustomerListResponse</a></code>
- <code title="delete /customers/{customer_id}">client.customers.<a href="./src/autumn/resources/customers.py">delete</a>(customer_id) -> <a href="./src/autumn/types/customer_delete_response.py">CustomerDeleteResponse</a></code>
- <code title="get /customers/{customer_id}">client.customers.<a href="./src/autumn/resources/customers.py">get</a>(customer_id, \*\*<a href="src/autumn/types/customer_get_params.py">params</a>) -> <a href="./src/autumn/types/shared/customer.py">Customer</a></code>

# Plans

Types:

```python
from autumn.types import PlanListResponse, PlanDeleteResponse
```

Methods:

- <code title="post /plans">client.plans.<a href="./src/autumn/resources/plans.py">create</a>(\*\*<a href="src/autumn/types/plan_create_params.py">params</a>) -> <a href="./src/autumn/types/shared/plan.py">Plan</a></code>
- <code title="post /plans/{plan_id}">client.plans.<a href="./src/autumn/resources/plans.py">update</a>(plan_id, \*\*<a href="src/autumn/types/plan_update_params.py">params</a>) -> <a href="./src/autumn/types/shared/plan.py">Plan</a></code>
- <code title="get /plans">client.plans.<a href="./src/autumn/resources/plans.py">list</a>(\*\*<a href="src/autumn/types/plan_list_params.py">params</a>) -> <a href="./src/autumn/types/plan_list_response.py">PlanListResponse</a></code>
- <code title="delete /plans/{plan_id}">client.plans.<a href="./src/autumn/resources/plans.py">delete</a>(plan_id, \*\*<a href="src/autumn/types/plan_delete_params.py">params</a>) -> <a href="./src/autumn/types/plan_delete_response.py">PlanDeleteResponse</a></code>
- <code title="get /plans/{plan_id}">client.plans.<a href="./src/autumn/resources/plans.py">get</a>(plan_id) -> <a href="./src/autumn/types/shared/plan.py">Plan</a></code>

# Entities

Types:

```python
from autumn.types import EntityDeleteResponse
```

Methods:

- <code title="post /customers/{customer_id}/entities">client.entities.<a href="./src/autumn/resources/entities.py">create</a>(customer_id, \*\*<a href="src/autumn/types/entity_create_params.py">params</a>) -> <a href="./src/autumn/types/shared/entity.py">Entity</a></code>
- <code title="delete /customers/{customer_id}/entities/{entity_id}">client.entities.<a href="./src/autumn/resources/entities.py">delete</a>(entity_id, \*, customer_id) -> <a href="./src/autumn/types/entity_delete_response.py">EntityDeleteResponse</a></code>
- <code title="get /customers/{customer_id}/entities/{entity_id}">client.entities.<a href="./src/autumn/resources/entities.py">get</a>(entity_id, \*, customer_id, \*\*<a href="src/autumn/types/entity_get_params.py">params</a>) -> <a href="./src/autumn/types/shared/entity.py">Entity</a></code>

# Referrals

Types:

```python
from autumn.types import ReferralCreateCodeResponse, ReferralRedeemCodeResponse
```

Methods:

- <code title="post /referrals/code">client.referrals.<a href="./src/autumn/resources/referrals.py">create_code</a>(\*\*<a href="src/autumn/types/referral_create_code_params.py">params</a>) -> <a href="./src/autumn/types/referral_create_code_response.py">ReferralCreateCodeResponse</a></code>
- <code title="post /referrals/redeem">client.referrals.<a href="./src/autumn/resources/referrals.py">redeem_code</a>(\*\*<a href="src/autumn/types/referral_redeem_code_params.py">params</a>) -> <a href="./src/autumn/types/referral_redeem_code_response.py">ReferralRedeemCodeResponse</a></code>

# Balances

Types:

```python
from autumn.types import BalanceUpdateResponse
```

Methods:

- <code title="post /balances/update">client.balances.<a href="./src/autumn/resources/balances.py">update</a>(\*\*<a href="src/autumn/types/balance_update_params.py">params</a>) -> <a href="./src/autumn/types/balance_update_response.py">BalanceUpdateResponse</a></code>

# Events

Types:

```python
from autumn.types import EventListResponse, EventAggregateResponse
```

Methods:

- <code title="post /events/list">client.events.<a href="./src/autumn/resources/events.py">list</a>(\*\*<a href="src/autumn/types/event_list_params.py">params</a>) -> <a href="./src/autumn/types/event_list_response.py">EventListResponse</a></code>
- <code title="post /events/aggregate">client.events.<a href="./src/autumn/resources/events.py">aggregate</a>(\*\*<a href="src/autumn/types/event_aggregate_params.py">params</a>) -> <a href="./src/autumn/types/event_aggregate_response.py">EventAggregateResponse</a></code>
