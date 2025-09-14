
import pathlib, shutil, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

def copy_if(src, dst):
    p = ROOT / src
    if p.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)

def to_tex(csv_rel, tex_rel, caption, label):
    p = ROOT / csv_rel
    if p.exists():
        df = pd.read_csv(p)
        tex = df.to_latex(index=False, escape=True, caption=caption, label=label)
        out = ROOT / tex_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(tex, encoding="utf-8")

def main():
    copy_if("reports/tables/fe_main.csv", ART/"tables/fe_main.csv")
    copy_if("reports/tables/iv_main.txt", ART/"tables/iv_main.txt")
    copy_if("reports/tables/did_event.csv", ART/"tables/did_event.csv")
    copy_if("reports/tables/mediation.csv", ART/"tables/mediation.csv")
    copy_if("reports/figures/eventstudy.png", ART/"figures/eventstudy.png")
    copy_if("data/processed/firm_quarter.csv", ART/"data/firm_quarter.csv")

    to_tex("reports/tables/fe_main.csv", "artifacts/tables/fe_main.tex", "Fixed-effects regression", "tab:fe_main")
    to_tex("reports/tables/did_event.csv", "artifacts/tables/did_event.tex", "Event-study coefficients", "tab:eventstudy")
    to_tex("reports/tables/mediation.csv", "artifacts/tables/mediation.tex", "Statistical mediation", "tab:mediation")

    print("[OK] Artifacts updated under artifacts/")

if __name__ == "__main__":
    main()
