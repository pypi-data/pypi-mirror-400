from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScopeStackNode:
    scope_index: int
    tail: ScopeStackNode | None


@dataclass(frozen=True, slots=True)
class SymbolStackNode:
    symbol_id: int
    scopes: ScopeStackNode | None
    tail: SymbolStackNode | None


@dataclass(frozen=True, slots=True)
class StackState:
    symbol_stack: SymbolStackNode | None
    scope_stack: ScopeStackNode | None
