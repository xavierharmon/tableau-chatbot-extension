import io
import re
import pandas as pd


class FileHandler:

    FULL_ROW_LIMIT = 30   # Send all rows below this
    SAMPLE_SIZE    = 30   # If above limit, sample this many evenly

    def parse(self, file_bytes: bytes, filename: str, field_context: str = "") -> dict:
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
            "data_context": self.build_data_context(df, columns, filename, sheet_name, field_context)
        }

    @staticmethod
    def sanitize(val) -> str:
        val = str(val)[:60]
        val = re.sub(r'[\\"\r\n\t]', ' ', val)
        val = re.sub(r'[^\x20-\x7E]', '', val)
        return val.strip()

    def build_data_context(self, df: pd.DataFrame, columns: list, file_name: str, sheet_name: str, field_context: str = "") -> str:
        total_rows = len(df)
        col_stats  = []

        for col in columns:
            series     = df[col].replace("", pd.NA).dropna()
            if len(series) == 0:
                continue
            numeric    = pd.to_numeric(series, errors="coerce").dropna()
            is_numeric = len(numeric) / len(series) > 0.8

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
                ellipsis = "..." if len(unique) > 8 else ""
                col_stats.append(
                    f"{self.sanitize(col)} [text]: {len(unique)} unique values - e.g. {preview}{ellipsis}"
                )

        # Smart row limit — all rows under threshold, even sample above
        if total_rows <= self.FULL_ROW_LIMIT:
            data_df  = df
            data_label = f"DATA (all {total_rows:,} rows)"
        else:
            step     = total_rows // self.SAMPLE_SIZE
            data_df  = df.iloc[::step].head(self.SAMPLE_SIZE)
            data_label = f"DATA (evenly sampled {len(data_df)} of {total_rows:,} rows)"

        header_row = " | ".join(self.sanitize(c) for c in columns)
        data_rows  = "\n".join(
            " | ".join(self.sanitize(str(row[col]))[:40] for col in columns)
            for _, row in data_df.iterrows()
        )

        parts = [
            f"FILE: {file_name} (Sheet: \"{sheet_name}\")",
            f"TOTAL ROWS: {total_rows:,} | COLUMNS: {len(columns)}",
        ]

        # Inject field context from markdown if provided
        if field_context and field_context.strip():
            parts += [
                "",
                "FIELD CONTEXT & BUSINESS RULES:",
                field_context.strip(),
            ]

        parts += [
            "",
            "COLUMN STATISTICS:",
            "\n".join(col_stats),
            "",
            f"{data_label}:",
            header_row,
            data_rows,
        ]

        return "\n".join(parts).strip()