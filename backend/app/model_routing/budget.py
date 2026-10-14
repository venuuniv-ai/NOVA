from datetime import UTC
from decimal import ROUND_CEILING, Decimal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.model_routing.models import BudgetDay
from app.model_routing.policy import requires_budget, upper_bound_cost


def money(value):
    return Decimal(value).quantize(Decimal("0.0000000001"), rounding=ROUND_CEILING)


class BudgetPolicy:
    def __init__(self, daily=Decimal(0), per_request=Decimal(0)):
        self.daily, self.per_request = money(daily), money(per_request)

    def reserve(self, session, call, spec, request, now):
        if not requires_budget(spec):
            return True
        estimate = upper_bound_cost(spec, request.max_output_tokens)
        if estimate is None or money(estimate) + call.accounted_cost_usd > self.per_request:
            return False
        day = now.astimezone(UTC).date()
        session.execute(
            insert(BudgetDay)
            .values(user_id=request.user_id, day=day, consumed_usd=0, reserved_usd=0)
            .on_conflict_do_nothing()
        )
        budget = session.scalar(
            select(BudgetDay)
            .where(BudgetDay.user_id == request.user_id, BudgetDay.day == day)
            .with_for_update()
        )
        amount = money(estimate)
        if budget.consumed_usd + budget.reserved_usd + amount > self.daily:
            return False
        budget.reserved_usd += amount
        call.reserved_cost_usd, call.reserved_day = amount, day
        return True

    def settle(self, session, call, actual=None):
        if not call.reserved_day:
            return
        budget = session.scalar(
            select(BudgetDay)
            .where(BudgetDay.user_id == call.user_id, BudgetDay.day == call.reserved_day)
            .with_for_update()
        )
        reserved = call.reserved_cost_usd
        budget.reserved_usd -= reserved
        # Unknown outcomes may still have been billed: retain the upper bound, never refund blindly.
        accounted = reserved if actual is None else min(money(actual), reserved)
        budget.consumed_usd += accounted
        call.accounted_cost_usd += accounted
        call.reserved_cost_usd = Decimal(0)
        call.reserved_day = None
