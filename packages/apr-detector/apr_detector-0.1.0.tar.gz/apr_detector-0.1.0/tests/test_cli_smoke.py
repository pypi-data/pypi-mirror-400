from apr_detector.cli import main


def test_cli_smoke(tmp_path, chr1_prefix):
    fasta_path = tmp_path / "Chr1_subset.fasta"
    fasta_path.write_text(f">Chr1_subset\n{chr1_prefix}\n", encoding="utf-8")
    output_dir = tmp_path / "out"

    args = [
        "Model2",
        "-i",
        str(fasta_path),
        "-o",
        str(output_dir),
        "-nt",
    ]
    main(args)

    output_file = output_dir / "Chr1_subset_APRs.tsv"
    assert output_file.exists()
    first_line = output_file.read_text(encoding="utf-8").splitlines()[0]
    assert first_line.startswith("# MODEL=")
