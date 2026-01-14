from apibean.jupyter.cli import build_parser, run_from_args

def main():
    parser = build_parser()

    # codemind add it's own options
    parser.prog = "codemind"
    parser.add_argument(
        "--codemind-mode",
        choices=["dev", "prod"],
        default="dev",
    )

    args = parser.parse_args()

    # codemind process it's own options
    if args.codemind_mode == "prod":
        print("🔒 codemind running in prod mode")

    # delegate apibean-jupyter
    run_from_args(args)
