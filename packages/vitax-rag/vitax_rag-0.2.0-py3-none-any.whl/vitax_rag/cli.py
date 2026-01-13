import sys
import argparse
import torch
import numpy as np
import copy
import os
from distutils.util import strtobool
from Bio import SeqIO
from tqdm import tqdm

from vitax_rag.utils import get_resource_path
from vitax_rag.model.model_vitax import Encoder
from vitax_rag.model.tokenizer_hyena import CharacterTokenizer
from vitax_rag.lca.tree import (
    load_node,
    convert_node_to_treenode,
    add_values_node,
    max_leaf_sum2,
)
from vitax_rag.utils import (
    run_blast,
    find_blast_augument,
    split_string,
)


def parse_bool(x):
    return bool(strtobool(str(x)))


def reverse_complement(dna):
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    complemented = ''.join(complement.get(base, base) for base in dna)
    return complemented[::-1]


def validate_data_dir(data_dir):
    """
    Expected structure:
    data_dir/
      ├── blast/
      │   └── blastdb.{nin,nsq,nhr}
      └── sequence/
    """
    blast_db_prefix = os.path.join(data_dir, "blast", "blastdb")

    required_exts = [".nin", ".nsq", ".nhr"]
    missing = [
        blast_db_prefix + ext
        for ext in required_exts
        if not os.path.exists(blast_db_prefix + ext)
    ]

    if missing:
        print("❌ BLAST database files not found:")
        for f in missing:
            print(f"  - {f}")
        sys.exit(1)

    return blast_db_prefix


def main():
    parser = argparse.ArgumentParser(
        description="ViTax-RAG: dsDNA virus genus-level classification"
    )

    parser.add_argument(
        "--contigs",
        default="test_contigs.fasta",
        help="FASTA file of contigs"
    )

    # ===== Model resources (packaged) =====
    parser.add_argument(
        '--model',
        default=None,
        help="Path to taxonomy belief tree (default: <data_dir>/model_save/model_weight.pth)")

    parser.add_argument(
        '--kmeans',
        default=None,
        help="Path to taxonomy belief tree (default: <data_dir>/odel_save/kmeans.pickle)")

    parser.add_argument(
        '--tree',
        default=None,
        help="Path to taxonomy belief tree (default: <data_dir>/model_save/tbt.pickle)")

    parser.add_argument(
        '--index',
        default=None,
        help="Path to taxonomy belief tree (default: <data_dir>/model_save/index.pickle)")

    # ===== Output & inference =====
    parser.add_argument("--out", default="output.txt", help="Output prediction file")
    parser.add_argument("--confidence", type=float, default=0.6, help="Confidence threshold")
    parser.add_argument("--window_size", type=int, default=400, help="Sliding step size")
    parser.add_argument("--chunk_size", type=int, default=2000, help="Chunk size")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size")
    parser.add_argument("--rc", type=parse_bool, default=True, help="Use reverse-complement")
    parser.add_argument("--augment", type=parse_bool, default=True, help="Use BLAST augmentation")
    parser.add_argument("--augment_len", type=int, default=4000, help="Augmentation length")

    # ===== External data (explicit) =====
    parser.add_argument(
        "--data_dir",
        required=True,
        help=(
            "Directory containing external resources.\n"
            "Expected structure:\n"
            "  data_dir/\n"
            "    └── blast/blastdb.*"
        )
    )
    parser.add_argument(
        "--blast_tmp",
        default="blast_temp_out",
        help="Temporary directory for BLAST output"
    )

    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Device selection"
    )

    args = parser.parse_args()
    
    model_dir = os.path.join(args.data_dir, "model_save")

    args.model = args.model or os.path.join(model_dir, "model_weight.pth")
    args.kmeans = args.kmeans or os.path.join(model_dir, "kmeans.pickle")
    args.tree = args.tree or os.path.join(model_dir, "tbt.pickle")
    args.index = args.index or os.path.join(model_dir, "index.pickle")


    # ===== Device =====
    if args.device == "cuda" and not torch.cuda.is_available():
        device = torch.device("cpu")
    elif args.device == "cpu":
        device = torch.device("cpu")
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # ===== Validate external data =====
    blast_db = validate_data_dir(args.data_dir)

    # ===== Load resources =====
    node = load_node(args.tree)
    kmean = load_node(args.kmeans)
    kmean.cluster_centers_ = kmean.cluster_centers_.astype(np.float64)
    index = load_node(args.index)
    node = convert_node_to_treenode(node)

    model = Encoder().to(device)
    state = torch.load(args.model, map_location=device)
    model.load_state_dict(state, strict=False)
    model.eval()

    dnatokenizer = CharacterTokenizer(
        characters=["A", "C", "G", "T", "N"],
        model_max_length=32770,
        add_special_tokens=False,
        padding_side="left",
    )

    results = []

    # ===== BLAST augmentation =====
    if args.augment:
        run_blast(args.contigs, args.blast_tmp, blast_db)

    with torch.no_grad():
        for record in tqdm(SeqIO.parse(args.contigs, "fasta")):
            tbt = copy.deepcopy(node)
            sequence_id = record.id
            sequence = str(record.seq)

            if args.augment:
                sequence = find_blast_augument(
                    sequence,
                    sequence_id,
                    args.blast_tmp,
                    args.augment_len,
                )

            dnas = split_string(
                sequence,
                chunk_size=args.chunk_size,
                step_size=args.window_size,
            )
            lendna = len(dnas) * (2 if args.rc else 1)

            inds = []
            for i in range(0, len(dnas), args.batch_size):
                batch = dnas[i:i + args.batch_size]
                ids = dnatokenizer(batch, padding=True, return_tensors="pt")[
                    "input_ids"
                ].to(device)
                embedding = model(ids)
                ind = kmean.predict(embedding.cpu().numpy().tolist())
                inds.extend(ind)


            if args.rc:
                rc_dnas = split_string(
                    reverse_complement(sequence),
                    chunk_size=args.chunk_size,
                    step_size=args.window_size,
                )
                for i in range(0, len(rc_dnas), args.batch_size):
                    batch = rc_dnas[i:i + args.batch_size]
                    ids = dnatokenizer(batch, padding=True, return_tensors="pt")[
                        "input_ids"
                    ].to(device)
                    embedding = model(ids)
                    ind = kmean.predict(embedding.cpu().numpy().tolist())
                    inds.extend(ind)

            add_values_node(tbt, index, inds)
            max_sum, leaf = max_leaf_sum2(
                tbt["root"],
                confidence=args.confidence,
                length=lendna,
            )
            belief = (max_sum / lendna) if lendna > 0 else 0.0
            pname = (
                "unclassified"
                if getattr(leaf, "level", "root") == "root"
                else f"{leaf.name}_{leaf.level}"
            )
            results.append(f"{sequence_id} {pname} {belief:.2f}")

    with open(args.out, "w", encoding="utf-8") as f:
        for s in results:
            f.write(s + "\n")

    print("✅ Done. Output written to:", args.out)


if __name__ == "__main__":
    main()
