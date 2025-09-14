
import argparse, re
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fin', required=True)
    ap.add_argument('--gscpi', required=True)
    args = ap.parse_args()

    quarter_re = re.compile(r'^\d{4}Q[1-4]$')

    fin_schema = DataFrameSchema({
        "firm_id": Column(str, nullable=False),
        "quarter": Column(str, checks=Check(lambda s: s.str.match(quarter_re).all()), nullable=False),
        "industry": Column(object, nullable=True),
        "sales": Column(float, nullable=False),
        "cogs": Column(float, nullable=False),
        "inventory": Column(float, nullable=False),
        "receivables": Column(float, nullable=False),
        "payables": Column(float, nullable=False),
    }, coerce=True)

    gscpi_schema = DataFrameSchema({
        "quarter": Column(str, checks=Check(lambda s: s.str.match(quarter_re).all()), nullable=False),
        "gscpi": Column(float, nullable=False),
    }, coerce=True)

    fin = pd.read_csv(args.fin)
    g = pd.read_csv(args.gscpi)

    fin_schema.validate(fin, lazy=True)
    gscpi_schema.validate(g, lazy=True)

    print("Validation OK: schemas look good. Rows:", len(fin), len(g))

if __name__ == '__main__':
    main()
