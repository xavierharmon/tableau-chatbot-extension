import pandas as pd


class ContextManager:
    """
    Loads role definitions from context_config.xlsx and provides
    role-aware system prompt context for the Groq agent.

    Future: swap load_from_excel() for load_from_active_directory()
    or load_from_tableau() without changing the rest of the app.
    """

    DEFAULT_ROLE = "viewer"

    def __init__(self):
        self.roles: dict = {}   # { role_id: { display_name, tone, detail_level, instructions, focus_areas } }
        self.active_role: str = self.DEFAULT_ROLE

    # ── Loaders ───────────────────────────────────────────────────────────────
    def load_from_excel(self, path: str):
        """Load role definitions from the Roles sheet of context_config.xlsx."""
        df = pd.read_excel(path, sheet_name="Roles", header=3)
        df.columns = ["role_id", "display_name", "tone", "detail_level", "instructions", "focus_areas"]
        df = df.dropna(subset=["role_id"])

        self.roles = {}
        for _, row in df.iterrows():
            rid = str(row["role_id"]).strip().lower()
            self.roles[rid] = {
                "display_name": str(row["display_name"]).strip(),
                "tone":         str(row["tone"]).strip(),
                "detail_level": str(row["detail_level"]).strip(),
                "instructions": str(row["instructions"]).strip(),
                "focus_areas":  str(row["focus_areas"]).strip() if pd.notna(row["focus_areas"]) else ""
            }

    def load_defaults(self):
        """Fallback hardcoded roles if no config file is provided."""
        self.roles = {
            "executive": {
                "display_name": "Executive / Leadership",
                "tone":         "Concise, strategic, confident",
                "detail_level": "High-level summaries only. Lead with the bottom line.",
                "instructions": "Focus on KPIs, trends, and business impact. Highlight anomalies or risks. Use plain language.",
                "focus_areas":  "Revenue trends, performance vs targets, risk flags"
            },
            "manager": {
                "display_name": "Manager",
                "tone":         "Balanced, practical, action-oriented",
                "detail_level": "Moderate detail with supporting data. Surface actionable insights.",
                "instructions": "Provide context around numbers. Highlight what needs attention. Use tables for comparisons.",
                "focus_areas":  "Team metrics, operational performance, budget vs actuals"
            },
            "viewer": {
                "display_name": "Viewer / Read-only",
                "tone":         "Friendly, clear, educational",
                "detail_level": "Simple and straightforward. Explain terms if needed.",
                "instructions": "Answer only what is asked. Use plain language. Avoid acronyms unless explained.",
                "focus_areas":  "Basic lookups, simple summaries"
            }
        }

    # ── Role management ───────────────────────────────────────────────────────
    def set_role(self, role_id: str):
        if role_id in self.roles:
            self.active_role = role_id
        else:
            self.active_role = self.DEFAULT_ROLE

    def get_role(self) -> dict:
        return self.roles.get(self.active_role, self.roles.get(self.DEFAULT_ROLE, {}))

    def get_roles_list(self) -> list:
        """Return list of { id, display_name } for the UI dropdown."""
        return [
            {"id": rid, "display_name": r["display_name"]}
            for rid, r in self.roles.items()
        ]

    # ── Prompt builder ────────────────────────────────────────────────────────
    def build_role_context(self) -> str:
        """Returns a formatted string injected into the system prompt."""
        role = self.get_role()
        if not role:
            return ""

        lines = [
            "ROLE CONTEXT:",
            f"  User Role:     {role['display_name']}",
            f"  Tone:          {role['tone']}",
            f"  Detail Level:  {role['detail_level']}",
            f"  Instructions:  {role['instructions']}",
        ]
        if role.get("focus_areas"):
            lines.append(f"  Focus Areas:   {role['focus_areas']}")

        return "\n".join(lines)