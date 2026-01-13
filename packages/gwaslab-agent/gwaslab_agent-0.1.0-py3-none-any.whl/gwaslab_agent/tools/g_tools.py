HARMONIZER_SET = {
    "harmonize",
    "basic_check",
    "assign_rsid",
    "assign_rsid2",
    "infer_af",
    "check_af",
    "check_data_consistency",
    "check_sanity",
    "fix_allele",
    "fix_chr",
    "fix_id",
    "fix_pos",
    "flip_allele_stats",
    "flip_snpid",
    "infer_strand",
    "infer_strand2",
    "liftover",
    "normalize_allele",
    "remove_dup",
    "sort_column",
    "sort_coordinate",
    "strip_snpid",
}

DOWNSTREAM_SET = {
    "estimate_h2_by_ldsc",
    "clump",
    "estimate_partitioned_h2_by_ldsc",
    "estimate_h2_cts_by_ldsc",
}

PLOTTER_SET = {
    "plot_mqq"
}
# "plot_associations"
#    "plot_manhattan",
#    "plot_qq",
#    "plot_region",
#    "plot_snp_density",

FILTERER_SET = {
    "filter_value",
    "filter_snp",
    "filter_indel",
    "filter_palindromic",
    "filter_region",
    "filter_flanking",
    "filter_flanking_by_chrpos",
    "filter_by_region",
    "filter_hapmap3",
    "random_variants",
    "search",
    "exclude_hla"
}


EXCLUDED_WRAPPERS_FROM_PRINTING = {
    "write_todos"
}
#    "get_associations",
UTILITY_SET = {
    "check_sumstats_qc_status",
    "fill_data",
    "get_density",
    "get_ess",
    "get_gc",
    "get_lead",
    "get_top",
    "get_novel",
    "get_per_snp_r2",
    "get_proxy",
    "view_sumstats",
    "infer_ancestry",
    "infer_build",
    "lookup_status",
    "set_build",
    "summary",
    "to_format"
}

EXCLUDED_SUMSTATS_METHODS = {
    "run_scdrs",
    "run_prscs",
    "run_magma",
    "get_ld_matrix_from_vcf",
    "abf_finemapping",
    "filter_in",
    "filter_out",
    "filter_region_in",
    "filter_region_out",
    "anno_gene",
    "align_with_template",
    "calculate_ld_matrix",
    "check_ref",
    "extract_ld_matrix",
    "plot_pipcs",
    "reload",
    "annotate_genes",
    "annotate_sumstats",
    "get_beta",
    "read_pipcs",
    "calculate_prs",
    "check_cs_overlap",
    "infer_eaf_from_maf",
    "infer_af",
    "check_af",
    "get_cs_lead",
    "offload",
    "run_susie_rss",
    "estimate_rg_by_ldsc",
    "check_novel_set",
    "check_cis",
    "plot_gwheatmap",
    "rsid_to_chrpos",
    "rsid_to_chrpos2",
   "check_id"
}
