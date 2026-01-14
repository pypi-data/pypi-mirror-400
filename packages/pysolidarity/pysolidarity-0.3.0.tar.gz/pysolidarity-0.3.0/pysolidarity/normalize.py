from __future__ import annotations

def strip_plus_tag(email: str) -> str:
    """
    Return email with any +tag in the local-part removed.
    Examples:
      "a+b@ex.com" -> "a@ex.com"
      "john.smith+volunteer@domain.org" -> "john.smith@domain.org"

    If the value doesn't look like a typical "local@domain", it is returned unchanged.
    """
    if not email:
        return email
    e = email.strip()
    if "@" not in e:
        return e
    local, _, domain = e.partition("@")
    if not local or not domain:
        return e
    plus = local.find("+")
    if plus != -1:
        local = local[:plus]
    return f"{local}@{domain}"
