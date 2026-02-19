"""
OMEGA Company Handlers
"""
from .get_dashboard import handle_get_omega_dashboard
from .get_resellers import handle_get_resellers
from .get_clients import handle_get_clients
from .get_revenue import handle_get_revenue
from .get_activity import handle_get_activity

__all__ = [
    "handle_get_omega_dashboard",
    "handle_get_resellers",
    "handle_get_clients",
    "handle_get_revenue",
    "handle_get_activity"
]
