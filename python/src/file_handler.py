import io
import re
import pandas as pd


class FileHandler:

    def parse(self, file_bytes: bytes, filename: str) -> dict:
        """Parse an uploaded Excel or CSV file and return structured data."""
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
            sheet_name = "Sheet1"
        else:
            xf = pd.ExcelFile(io.BytesIO(file_bytes))
            sheet_name = xf.sheet_names[0]
            df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name)

        df = df.fillna("")
        rows    = df.to_dict(orient="records")
        columns = list(df.columns)

        return {
            "rows":         rows,
            "columns":      columns,
            "sheet_name":   sheet_name,
            "file_name":    filename,
            "data_context": self.build_data_context(df, columns, filename, sheet_name)
        }

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def sanitize(val) -> str:
        val = str(val)[:60]
        val = re.sub(r'[\\"\r\n\t]', ' ', val)
        val = re.sub(r'[^\x20-\x7E]', '', val)
        return val.strip()

    def build_data_context(self, df: pd.DataFrame, columns: list, file_name: str, sheet_name: str) -> str:
        total_rows = len(df)
        col_stats  = []

        for col in columns:
            series    = df[col].replace("", pd.NA).dropna()
            numeric   = pd.to_numeric(series, errors="coerce").dropna()
            is_numeric = len(numeric) / len(series) > 0.8 if len(series) else False

            if is_numeric and len(numeric):
                col_stats.append(
                    f"{self.sanitize(col)} [numeric]: "
                    f"min={numeric.min()}, max={numeric.max()}, "
                    f"avg={numeric.mean():.2f}, sum={numeric.sum():.2f}, "
                    f"count={len(numeric)}"
                )
            else:
                unique  = series.unique()
                preview = ", ".join(str(v)[:30] for v in unique[:8])
                ellipsis = "…" if len(unique) > 8 else ""
                col_stats.append(
                    f"{self.sanitize(col)} [text]: {len(unique)} unique values — e.g. {preview}{ellipsis}"
                )

        # Sample rows
        sample_df  = df.head(60) if total_rows > 70 else df
        header_row = " | ".join(self.sanitize(c) for c in columns)
        data_rows  = "\n".join(
            " | ".join(self.sanitize(str(row[c]))[:40] for c in columns)
            for _, row in sample_df.iterrows()
        )

        return (
            f"FILE: {file_name} (Sheet: \"{sheet_name}\")\n"
            f"TOTAL ROWS: {total_rows:,} | COLUMNS: {len(columns)}\n\n"
            f"COLUMN STATISTICS:\n" + "\n".join(col_stats) + "\n\n"
            f"SAMPLE DATA ({len(sample_df)} rows shown):\n"
            f"{header_row}\n{data_rows}"
        ).strip()