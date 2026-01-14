#!/usr/bin/env python3
"""
rna_master_tools.py
Single-file advanced RNA-seq toolkit + CLI.

Usage examples:
    python rna_master_tools.py run-rmats --b1 a1.bam,a2.bam --b2 b1.bam,b2.bam --gtf ref.gtf --outdir rmats_out
    python rna_master_tools.py parse-rmats --in rmats_out/SE.MATS.JCEC.txt --out rmats_parsed.tsv
    python rna_master_tools.py run-starfusion --left left.fq --right right.fq --genome_lib_dir GRCh38_ctat_lib --outdir fusion_out
    python rna_master_tools.py compute-wgcna --counts counts_normalized.tsv --out modules.tsv
    python rna_master_tools.py biomarkers --counts counts_normalized.tsv --labels samplesheet.tsv --out biomarker_report.tsv
"""

import os
import sys
import argparse
import logging
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import classification_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# -------------------------
# Utilities
# -------------------------
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def run_cmd(cmd, check=True):
    logger.info("Run cmd: %s", " ".join(cmd))
    try:
        res = subprocess.run(cmd, check=check, capture_output=True, text=True)
        logger.debug("stdout: %s", res.stdout[:200])
        logger.debug("stderr: %s", res.stderr[:200])
        return res
    except subprocess.CalledProcessError as e:
        logger.error("Command failed: %s", e.stderr)
        raise

def read_table(path, index_col=None):
    return pd.read_csv(path, sep="\t", index_col=index_col)

def write_table(df, path):
    df.to_csv(path, sep="\t", index=True)

# -------------------------
# rMATS wrappers & parsers
# -------------------------
def run_rmats_cli(b1_list, b2_list, gtf, outdir, readlen=100, threads=8, rmats_cmd="rmats.py"):
    """
    Run rMATS CLI. b1_list/b2_list are comma-separated BAM paths strings.
    """
    ensure_dir(outdir)
    tmpdir = ensure_dir(os.path.join(outdir, "tmp"))
    cmd = [
        rmats_cmd,
        "--b1", b1_list,
        "--b2", b2_list,
        "--gtf", gtf,
        "--od", outdir,
        "--tmp", tmpdir,
        "--readLength", str(readlen),
        "--nthread", str(threads)
    ]
    run_cmd(cmd)
    return outdir

def parse_rmats_event_table(event_file, out_tsv=None):
    """
    Parse rMATS event file and compute PSI means and dPSI.
    """
    df = pd.read_csv(event_file, sep="\t", low_memory=False)
    # helper
    def mean_psi(s):
        try:
            vals = [float(x) for x in str(s).split(",") if x not in (".", "", "NA")]
            return np.nanmean(vals) if len(vals)>0 else np.nan
        except:
            return np.nan
    if 'IncLevel1' in df.columns:
        df['PSI_group1'] = df['IncLevel1'].apply(mean_psi)
    if 'IncLevel2' in df.columns:
        df['PSI_group2'] = df['IncLevel2'].apply(mean_psi)
    if 'PSI_group1' in df and 'PSI_group2' in df:
        df['dPSI'] = df['PSI_group1'] - df['PSI_group2']
    for col in ['PValue','FDR']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    if out_tsv:
        df.to_csv(out_tsv, sep="\t", index=False)
    return df

def plot_rmats_volcano(df, out_png=None, fdr_thresh=0.05, dpsi_thresh=0.1):
    neglog = -np.log10(df['FDR'].replace(0,1e-300))
    sig = (df['FDR'] <= fdr_thresh) & (df['dPSI'].abs() >= dpsi_thresh)
    plt.figure(figsize=(7,6))
    plt.scatter(df['dPSI'], neglog, s=8, c='gray', alpha=0.7)
    if sig.any():
        plt.scatter(df.loc[sig,'dPSI'], neglog.loc[sig], s=10, c='red', alpha=0.8)
    plt.axvline(dpsi_thresh, color='blue', linestyle='--')
    plt.axvline(-dpsi_thresh, color='blue', linestyle='--')
    plt.axhline(-np.log10(fdr_thresh), color='green', linestyle='--')
    plt.xlabel('dPSI'); plt.ylabel('-log10(FDR)'); plt.title('rMATS volcano')
    if out_png:
        plt.savefig(out_png, dpi=150)
    return plt

# -------------------------
# STAR-Fusion wrapper & parser
# -------------------------
def run_star_fusion_cli(left_fq, right_fq, genome_lib_dir, outdir, threads=8):
    """
    Run STAR-Fusion. Assumes STAR-Fusion installed and in PATH or in container.
    """
    ensure_dir(outdir)
    cmd = [
        "STAR-Fusion",
        "--left_fq", left_fq,
        "--right_fq", right_fq,
        "--genome_lib_dir", genome_lib_dir,
        "--output_dir", outdir,
        "--CPU", str(threads)
    ]
    run_cmd(cmd)
    return outdir

def parse_star_fusion_tsv(fusion_tsv, out_tsv=None):
    df = pd.read_csv(fusion_tsv, sep="\t", comment='#', low_memory=False)
    if out_tsv:
        df.to_csv(out_tsv, sep="\t", index=False)
    return df

# -------------------------
# WGCNA-like coexpression (lightweight)
# -------------------------
def compute_wgcna_modules_cli(counts_tsv, out_tsv=None, soft_power=6):
    """
    counts_tsv: genes x samples (rows genes, columns samples) or samples x genes.
    We'll accept genes rows (index=gene).
    Returns DataFrame gene->module
    """
    df = pd.read_csv(counts_tsv, sep="\t", index_col=0)
    # ensure genes are rows
    if df.shape[0] < df.shape[1] and df.index.str.contains('ENS').any():
        # likely already genes x samples; keep
        pass
    # compute correlation between genes (use transpose if needed)
    expr = df
    # if many samples < genes, correlation across samples => gene-gene correlation requires samples dimension
    corr = expr.T.corr()  # gene x gene
    adj = np.abs(corr) ** soft_power
    # approximate TOM (simple)
    tom = adj * np.abs(corr)
    dist = 1 - tom
    # fill nans
    dist = dist.fillna(1.0)
    # clustering
    # AgglomerativeClustering does not accept distance matrix directly for fit_predict unless precomputed affinity
    clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=0.2, affinity='precomputed', linkage='average')
    labels = clustering.fit_predict(dist.values)
    modules = pd.DataFrame({'gene': corr.index, 'module': labels})
    if out_tsv:
        modules.to_csv(out_tsv, sep="\t", index=False)
    return modules

# -------------------------
# BIOMARKER SELECTION + ML
# -------------------------
def select_features_rf_cli(counts_tsv, labels_tsv, out_tsv=None, topk=50):
    """
    counts_tsv: genes x samples (index gene, columns samples) OR samples x genes.
    labels_tsv: must include columns sampleID, label
    We'll convert to samples x features for ML.
    """
    counts = pd.read_csv(counts_tsv, sep="\t", index_col=0)
    ss = pd.read_csv(labels_tsv, sep="\t")
    # convert to samples x genes if needed
    if counts.index[0].startswith('ENS') or counts.index[0].isalpha():
        # genes x samples -> transpose
        X = counts.T
    else:
        X = counts
    # align samples
    if 'sampleID' in ss.columns:
        ss = ss.set_index('sampleID')
    labels = ss.loc[X.index, ss.columns[-1]]  # last column is label
    # RF
    rf = RandomForestClassifier(n_estimators=500, random_state=42, n_jobs=1)
    rf.fit(X, labels)
    imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    top = imp.head(topk)
    if out_tsv:
        top.to_csv(out_tsv, sep="\t", header=['importance'])
    return top

def train_classifiers_cli(counts_tsv, labels_tsv, out_tsv=None, test_size=0.25):
    counts = pd.read_csv(counts_tsv, sep="\t", index_col=0)
    ss = pd.read_csv(labels_tsv, sep="\t")
    if counts.index[0].startswith('ENS') or counts.index[0].isalpha():
        X = counts.T
    else:
        X = counts
    if 'sampleID' in ss.columns:
        ss = ss.set_index('sampleID')
    y = ss.loc[X.index, ss.columns[-1]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    rf = RandomForestClassifier(n_estimators=400, random_state=42)
    rf.fit(X_train, y_train)
    pred = rf.predict(X_test)
    rep = classification_report(y_test, pred, output_dict=True)
    if out_tsv:
        pd.DataFrame(rep).to_csv(out_tsv, sep="\t")
    return rep

# -------------------------
# CLI: argparse dispatcher
# -------------------------
def build_parser():
    p = argparse.ArgumentParser(prog="rna_master_tools.py")
    sub = p.add_subparsers(dest="cmd")

    # rMATS run
    a = sub.add_parser("run-rmats")
    a.add_argument("--b1", required=True, help="Comma-separated BAMs for group1")
    a.add_argument("--b2", required=True, help="Comma-separated BAMs for group2")
    a.add_argument("--gtf", required=True)
    a.add_argument("--outdir", required=True)
    a.add_argument("--readlen", type=int, default=100)
    a.add_argument("--threads", type=int, default=8)
    a.add_argument("--rmats-cmd", default="rmats.py")

    # parse rMATS
    b = sub.add_parser("parse-rmats")
    b.add_argument("--in", dest="infile", required=True)
    b.add_argument("--out", dest="out", default=None)

    # plot rMATS volcano
    c = sub.add_parser("plot-rmats")
    c.add_argument("--in", dest="infile", required=True)
    c.add_argument("--out", dest="out", default=None)

    # STAR-Fusion run
    d = sub.add_parser("run-starfusion")
    d.add_argument("--left", required=True)
    d.add_argument("--right", required=True)
    d.add_argument("--genome_lib_dir", required=True)
    d.add_argument("--outdir", required=True)
    d.add_argument("--threads", type=int, default=8)

    # parse star-fusion
    e = sub.add_parser("parse-starfusion")
    e.add_argument("--in", dest="infile", required=True)
    e.add_argument("--out", dest="out", default=None)

    # WGCNA
    f = sub.add_parser("compute-wgcna")
    f.add_argument("--counts", required=True)
    f.add_argument("--out", dest="out", default=None)
    f.add_argument("--power", type=int, default=6)

    # biomarkers select
    g = sub.add_parser("biomarkers")
    g.add_argument("--counts", required=True)
    g.add_argument("--labels", required=True)
    g.add_argument("--out", dest="out", default=None)
    g.add_argument("--topk", type=int, default=50)

    # classifiers
    h = sub.add_parser("train-classifiers")
    h.add_argument("--counts", required=True)
    h.add_argument("--labels", required=True)
    h.add_argument("--out", dest="out", default=None)

    return p

def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)

    if args.cmd == "run-rmats":
        run_rmats_cli(args.b1, args.b2, args.gtf, args.outdir, readlen=args.readlen, threads=args.threads, rmats_cmd=args.rmats_cmd)
    elif args.cmd == "parse-rmats":
        parse_rmats_event_table(args.infile, out_tsv=args.out)
    elif args.cmd == "plot-rmats":
        df = parse_rmats_event_table(args.infile)
        plot_rmats_volcano(df, out_png=args.out)
    elif args.cmd == "run-starfusion":
        run_star_fusion_cli(args.left, args.right, args.genome_lib_dir, args.outdir, threads=args.threads)
    elif args.cmd == "parse-starfusion":
        parse_star_fusion_tsv(args.infile, out_tsv=args.out)
    elif args.cmd == "compute-wgcna":
        compute_wgcna_modules_cli(args.counts, out_tsv=args.out, soft_power=args.power)
    elif args.cmd == "biomarkers":
        select_features_rf_cli(args.counts, args.labels, out_tsv=args.out, topk=args.topk)
    elif args.cmd == "train-classifiers":
        train_classifiers_cli(args.counts, args.labels, out_tsv=args.out)
    else:
        p.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
