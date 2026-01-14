from typing import Literal, Final
CompanyType  = Literal["CT","NH","CK","BH"]
StatementStr = Literal["balance","income","cflow_direct","cflow_indirect"]
PeriodType   = Literal["year","quarter"]

STATEMENT_TO_INT: Final[dict[StatementStr, int]] = {
    "balance": 1, "income": 2, "cflow_direct": 3, "cflow_indirect": 4
}
