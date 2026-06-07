from __future__ import annotations

import argparse
from pathlib import Path

from .author_metadata import run_author_metadata_audit_command
from .baselines import run_baseline_evaluation_command
from .checksums import run_checksum_audit_command
from .claim_gate import inspect_manuscript
from .climate_features import run_climate_feature_command
from .config import load_study_config
from .data_access_plan import run_data_access_plan_command
from .data_access_templates import run_data_access_template_audit_command
from .data_catalog import format_source_table, sources_from_config
from .data_download import (
    fluxnet_download_instructions,
    run_era5_download_command,
    run_modis_download_command,
)
from .download_status import run_download_status_command
from .evidence import load_evidence_registry, render_evidence_status, run_evidence_artifact_audit_command
from .event_catalogue import run_event_catalogue_command
from .era5_raw_aggregate import run_era5_raw_aggregate_command
from .figures import render_figure_plan, run_figure_asset_generation_command
from .fluxnet_anomalies import run_fluxnet_anomaly_preprocess_command
from .fluxnet_raw import audit_fluxnet_raw_archives
from .fluxnet_validation import run_fluxnet_validation_command
from .manuscript_format import run_manuscript_format_audit_command
from .modis_anomalies import run_modis_anomaly_command
from .modis_quality import run_modis_quality_command
from .modis_raw import run_modis_raw_inventory_command
from .modeling_dataset import run_modeling_dataset_command
from .pilot_slice import run_minimum_evidence_slice_command
from .pilot_figures import run_pilot_figure_generation_command
from .placeholder_map import run_placeholder_map_command
from .provider_requests import run_provider_request_templates_command
from .public_release import run_public_release_audit_command
from .qc import render_e00_qc_report
from .readiness_dashboard import run_readiness_dashboard_command
from .references import run_reference_audit_command
from .reproducibility import run_reproducibility_audit_command
from .robustness import (
    run_biome_stratified_validation_command,
    run_placebo_validation_command,
    run_sensor_cross_validation_command,
    run_threshold_sensitivity_command,
)
from .precursor_discovery import run_precursor_discovery_command
from .predictive_validation import run_predictive_validation_summary_command
from .spatial_validation import run_spatial_validation_command
from .smoke import run_pipeline_smoke_test_command
from .submission_package import run_submission_package_audit_command
from .submission_gate import evaluate_submission_gate, render_submission_gate
from .temporal_validation import run_temporal_validation_command
from .uncertainty import run_uncertainty_audit_command
from .validation import validation_design_from_config


def era5_download(args: argparse.Namespace) -> int:
    month_list = None
    if args.months:
        month_list = [int(m.strip()) for m in args.months.split(",")]
    success, skipped, failed, log = run_era5_download_command(
        config_path=args.config,
        output_dir=args.output_dir,
        log_path=args.log,
        year_start=args.year_start,
        year_end=args.year_end,
        months=month_list,
        dry_run=args.dry_run,
        dataset_selection=args.only,
    )
    print(f"Success: {success}, Skipped: {skipped}, Failed: {failed}")
    print(f"Download log: {log}")
    return 0 if failed == 0 else 2


def modis_download(args: argparse.Namespace) -> int:
    success, skipped, failed, log = run_modis_download_command(
        config_path=args.config,
        output_dir=args.output_dir,
        log_path=args.log,
        year_start=args.year_start,
        year_end=args.year_end,
        tiles=args.tiles,
        dry_run=args.dry_run,
    )
    print(f"Success: {success}, Skipped: {skipped}, Failed: {failed}")
    print(f"Download log: {log}")
    return 0 if failed == 0 else 2


def modis_raw_inventory(args: argparse.Namespace) -> int:
    result = run_modis_raw_inventory_command(
        input_dir=args.input_dir,
        output_csv=args.output,
        output_report=args.report,
        start_year=args.start_year,
        end_year=args.end_year,
    )
    print(f"Wrote MODIS raw inventory CSV: {result.output_csv}")
    print(f"Wrote MODIS raw inventory report: {result.output_report}")
    print(f"Status: {result.status}")
    return 0 if result.found_expected_granules > 0 and result.suspicious_files == 0 else 2


def fluxnet_instructions(args: argparse.Namespace) -> int:
    print(fluxnet_download_instructions())
    return 0


def download_status(args: argparse.Namespace) -> int:
    report, output = run_download_status_command(args.log, args.output)
    print(f"Wrote download status report: {output}")
    print(f"Status: {report.status}")
    return 0 if report.ready_for_qc else 2


def describe_study(args: argparse.Namespace) -> int:
    config = load_study_config(args.config)
    print(config["project"]["working_title"])
    print()
    print(format_source_table(sources_from_config(config)))
    print()
    design = validation_design_from_config(config)
    print(f"Temporal holdout: {design.temporal_holdout_years[0]}-{design.temporal_holdout_years[1]}")
    print(f"Spatial holdout: {design.spatial_holdout}")
    print(f"External validation: {design.external_validation_source}")
    return 0


def check_claims(args: argparse.Namespace) -> int:
    report = inspect_manuscript(args.manuscript)
    print(f"Manuscript: {report.path}")
    print(f"RESULT_REQUIRED placeholders: {report.result_placeholders}")
    print(f"AUTHOR_REQUIRED placeholders: {report.author_placeholders}")
    print(f"DATA_ACCESS_REQUIRED placeholders: {report.data_placeholders}")
    return 0


def manuscript_format_audit(args: argparse.Namespace) -> int:
    report, output = run_manuscript_format_audit_command(
        manuscript_path=args.manuscript,
        output_path=args.output,
        journal=args.journal,
    )
    print(f"Wrote manuscript format audit: {output}")
    print(f"Status: {report.status}")
    return 0 if report.status == "READY_FOR_FORMAT_REVIEW" else 2


def submission_package_audit(args: argparse.Namespace) -> int:
    audit, output, csv_output = run_submission_package_audit_command(
        root=args.root,
        output_path=args.output,
        csv_path=args.csv,
    )
    print(f"Wrote submission package audit: {output}")
    print(f"Wrote submission package status CSV: {csv_output}")
    print(f"Status: {'READY' if audit.ready else 'NOT_READY'}")
    return 0 if audit.ready else 2


def readiness_dashboard(args: argparse.Namespace) -> int:
    dashboard, output, csv_output = run_readiness_dashboard_command(
        output_path=args.output,
        csv_path=args.csv,
        root=args.root,
        manuscript=args.manuscript,
        registry=args.registry,
        config=args.config,
        reference_metadata=args.reference_metadata,
    )
    print(f"Wrote readiness dashboard: {output}")
    print(f"Wrote readiness dashboard CSV: {csv_output}")
    print(f"Status: {'READY' if dashboard.ready else 'NOT_READY'}")
    return 0 if dashboard.ready else 2


def write_figure_plan(args: argparse.Namespace) -> int:
    output = Path(args.output)
    output.write_text(render_figure_plan() + "\n", encoding="utf-8")
    print(f"Wrote figure plan: {output}")
    return 0


def reference_audit(args: argparse.Namespace) -> int:
    report, output, status_csv = run_reference_audit_command(
        metadata_path=args.metadata,
        report_path=args.output,
        status_csv_path=args.status_csv,
    )
    print(f"Wrote reference audit: {output}")
    print(f"Wrote reference status CSV: {status_csv}")
    print(f"Status: {'READY' if report.ready else 'NOT_READY'}")
    return 0 if report.ready else 2


def author_metadata_audit(args: argparse.Namespace) -> int:
    audit, output, csv_output = run_author_metadata_audit_command(
        metadata_path=args.metadata,
        output_path=args.output,
        csv_path=args.csv,
    )
    print(f"Wrote author metadata audit: {output}")
    print(f"Wrote author metadata status CSV: {csv_output}")
    print(f"Status: {'READY' if audit.ready else 'NOT_READY'}")
    return 0 if audit.ready else 2


def generate_figure_assets(args: argparse.Namespace) -> int:
    fig1, manifest, report = run_figure_asset_generation_command(
        config_path=args.config,
        output_dir=args.output_dir,
        manifest_path=args.manifest,
        report_path=args.report,
    )
    print(f"Wrote Fig. 1 workflow schematic: {fig1}")
    print(f"Wrote figure manifest: {manifest}")
    print(f"Wrote figure generation report: {report}")
    return 0


def evidence_status(args: argparse.Namespace) -> int:
    report = load_evidence_registry(args.registry)
    print(render_evidence_status(report))
    return 0


def evidence_artifact_audit(args: argparse.Namespace) -> int:
    audit, output, csv_output = run_evidence_artifact_audit_command(
        registry_path=args.registry,
        root=args.root,
        output_path=args.output,
        csv_path=args.csv,
    )
    print(f"Wrote evidence artifact audit: {output}")
    print(f"Wrote evidence artifact audit CSV: {csv_output}")
    print(f"Status: {'READY' if audit.ready else 'NOT_READY'}")
    return 0 if audit.ready else 2


def checksum_audit(args: argparse.Namespace) -> int:
    audit, output, csv_output = run_checksum_audit_command(
        root=args.root,
        output_path=args.output,
        csv_path=args.csv,
    )
    print(f"Wrote data checksum audit: {output}")
    print(f"Wrote data checksum CSV: {csv_output}")
    print(f"Status: {'READY' if audit.ready else 'NOT_READY'}")
    return 0 if audit.ready else 2


def placeholder_map(args: argparse.Namespace) -> int:
    mapping, output, csv_output = run_placeholder_map_command(
        manuscript_path=args.manuscript,
        output_path=args.output,
        csv_path=args.csv,
    )
    print(f"Wrote placeholder evidence map: {output}")
    print(f"Wrote placeholder evidence CSV: {csv_output}")
    print(f"Status: {'READY' if mapping.complete else 'NOT_READY'}")
    return 0 if mapping.complete else 2


def reproducibility_audit(args: argparse.Namespace) -> int:
    audit, report, manifest = run_reproducibility_audit_command(
        report_path=args.output,
        command_manifest_path=args.command_manifest,
        environment_yml_path=args.environment_yml,
        requirements_lock_path=args.requirements_lock,
        seed_manifest_path=args.seed_manifest,
        compute_budget_path=args.compute_budget,
    )
    print(f"Wrote reproducibility audit: {report}")
    print(f"Wrote reproducibility command manifest: {manifest}")
    print(f"Status: {'READY' if audit.ready else 'NOT_READY'}")
    return 0 if audit.ready else 2


def pipeline_smoke_test(args: argparse.Namespace) -> int:
    result = run_pipeline_smoke_test_command(
        output_dir=args.output_dir,
        report_path=args.report,
        manifest_path=args.manifest,
        config_path=args.config,
    )
    print(f"Wrote synthetic pipeline smoke-test report: {result.report_path}")
    print(f"Wrote synthetic pipeline smoke-test manifest: {result.manifest_path}")
    print("Status: COMPLETE_FOR_SYNTHETIC_DATA")
    return 0


def data_access_plan(args: argparse.Namespace) -> int:
    manifest, report = run_data_access_plan_command(
        config_path=args.config,
        manifest_path=args.manifest,
        report_path=args.report,
    )
    print(f"Wrote data-access manifest: {manifest}")
    print(f"Wrote data-access report: {report}")
    return 0


def data_access_template_audit(args: argparse.Namespace) -> int:
    audit, output, csv_output = run_data_access_template_audit_command(
        root=args.root,
        output_path=args.output,
        csv_path=args.csv,
    )
    print(f"Wrote data-access template audit: {output}")
    print(f"Wrote data-access template status CSV: {csv_output}")
    print(f"Status: {'READY' if audit.ready else 'NOT_READY'}")
    return 0 if audit.ready else 2


def provider_request_templates(args: argparse.Namespace) -> int:
    artifacts, manifest, report = run_provider_request_templates_command(
        config_path=args.config,
        output_dir=args.output_dir,
        manifest_path=args.manifest,
        report_path=args.report,
    )
    print(f"Wrote provider request manifest: {manifest}")
    print(f"Wrote provider request report: {report}")
    for artifact in artifacts:
        print(f"Wrote {artifact.source} request template: {artifact.template_path}")
    print("Status: NOT_READY")
    return 2


def public_release_audit(args: argparse.Namespace) -> int:
    audit, output, csv_output = run_public_release_audit_command(
        root=args.root,
        output_path=args.output,
        csv_path=args.csv,
    )
    print(f"Wrote public release audit: {output}")
    print(f"Wrote public release status CSV: {csv_output}")
    print(f"Status: {'READY' if audit.ready else 'NOT_READY'}")
    return 0 if audit.ready else 2


def submission_gate(args: argparse.Namespace) -> int:
    report = evaluate_submission_gate(args.manuscript, args.registry)
    print(render_submission_gate(report))
    return 0 if report.ready else 2


def e00_data_qc(args: argparse.Namespace) -> int:
    report = render_e00_qc_report(args.config, args.registry, args.root)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(f"Wrote E00 data QC report: {output}")
    return 0


def e01_event_catalogue(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_event_catalogue_command(
        input_path=args.input,
        output_dir=args.output_dir,
        date_col=args.date_col,
        unit_col=args.unit_col,
        value_col=args.value_col,
        percentile=args.percentile,
        minimum_duration=args.minimum_duration,
    )
    if completed_for_input:
        print(f"Wrote E01 event catalogue artifacts in: {args.output_dir}")
    else:
        print(f"Wrote E01 readiness report: {report_path}")
    return 0


def modis_anomalies(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_modis_anomaly_command(
        input_path=args.input,
        output_path=args.output,
        report_path=args.report,
        min_climatology_samples=args.min_climatology_samples,
    )
    if completed_for_input:
        print(f"Wrote MODIS anomalies: {args.output}")
        print(f"Wrote anomaly QC report: {report_path}")
    else:
        print(f"Wrote MODIS anomaly readiness report: {report_path}")
    return 0


def modis_quality_filter(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_modis_quality_command(
        input_path=args.input,
        output_path=args.output,
        report_path=args.report,
        max_vi_usefulness=args.max_vi_usefulness,
    )
    if completed_for_input:
        print(f"Wrote quality-filtered MODIS table: {args.output}")
        print(f"Wrote MODIS quality QC report: {report_path}")
    else:
        print(f"Wrote MODIS quality readiness report: {report_path}")
    return 0


def era5_climate_features(args: argparse.Namespace) -> int:
    variable_override = None
    if args.variables:
        variable_override = tuple(variable.strip() for variable in args.variables.split(",") if variable.strip())
    completed_for_input, report_path = run_climate_feature_command(
        input_path=args.input,
        output_path=args.output,
        report_path=args.report,
        config_path=args.config,
        min_climatology_samples=args.min_climatology_samples,
        variables_override=variable_override,
    )
    if completed_for_input:
        print(f"Wrote ERA5 climate lag features: {args.output}")
        print(f"Wrote ERA5 feature QC report: {report_path}")
    else:
        print(f"Wrote ERA5 climate-feature readiness report: {report_path}")
    return 0


def era5_raw_aggregate(args: argparse.Namespace) -> int:
    result = run_era5_raw_aggregate_command(
        input_dir=args.input_dir,
        output_path=args.output,
        report_path=args.report,
        config_path=args.config,
        spatial_stride=args.spatial_stride,
    )
    print(f"Wrote ERA5 raw aggregate report: {result.report_path}")
    if result.completed_for_input:
        print(f"Wrote ERA5 composite climate table: {result.output_path}")
    print(f"Status: {result.status}")
    return 0 if result.completed_for_input else 2


def modeling_dataset(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_modeling_dataset_command(
        climate_path=args.climate,
        events_path=args.events,
        output_path=args.output,
        report_path=args.report,
        anomalies_path=args.anomalies,
    )
    if completed_for_input:
        print(f"Wrote modeling dataset: {args.output}")
        print(f"Wrote modeling dataset QC report: {report_path}")
    else:
        print(f"Wrote modeling dataset readiness report: {report_path}")
    return 0


def baseline_evaluation(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_baseline_evaluation_command(
        input_path=args.input,
        output_path=args.output,
        report_path=args.report,
        config_path=args.config,
    )
    if completed_for_input:
        print(f"Wrote baseline metrics: {args.output}")
        print(f"Wrote baseline evaluation report: {report_path}")
    else:
        print(f"Wrote baseline evaluation readiness report: {report_path}")
    return 0


def precursor_discovery(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_precursor_discovery_command(
        input_path=args.input,
        attribution_path=args.attribution,
        lag_response_path=args.lag_response,
        report_path=args.report,
    )
    if completed_for_input:
        print(f"Wrote feature attribution table: {args.attribution}")
        print(f"Wrote lag response summary: {args.lag_response}")
        print(f"Wrote precursor-discovery report: {report_path}")
    else:
        print(f"Wrote precursor-discovery readiness report: {report_path}")
    return 0


def temporal_holdout_validation(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_temporal_validation_command(
        modeling_path=args.modeling,
        candidates_path=args.candidates,
        output_path=args.output,
        report_path=args.report,
        config_path=args.config,
        top_n=args.top_n,
    )
    if completed_for_input:
        print(f"Wrote temporal holdout metrics: {args.output}")
        print(f"Wrote temporal validation report: {report_path}")
    else:
        print(f"Wrote temporal holdout readiness report: {report_path}")
    return 0


def spatial_holdout_validation(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_spatial_validation_command(
        modeling_path=args.modeling,
        candidates_path=args.candidates,
        output_path=args.output,
        report_path=args.report,
        region_col=args.region_col,
        top_n=args.top_n,
    )
    if completed_for_input:
        print(f"Wrote spatial holdout metrics: {args.output}")
        print(f"Wrote spatial validation report: {report_path}")
    else:
        print(f"Wrote spatial holdout readiness report: {report_path}")
    return 0


def fluxnet_validation(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_fluxnet_validation_command(
        fluxnet_path=args.fluxnet,
        windows_path=args.windows,
        output_path=args.output,
        report_path=args.report,
    )
    if completed_for_input:
        print(f"Wrote FLUXNET site anomaly metrics: {args.output}")
        print(f"Wrote FLUXNET validation report: {report_path}")
    else:
        print(f"Wrote FLUXNET validation readiness report: {report_path}")
    return 0


def fluxnet_raw_audit(args: argparse.Namespace) -> int:
    result = audit_fluxnet_raw_archives(
        input_dir=args.input_dir,
        output_csv=args.output,
        output_report=args.report,
    )
    print(f"Wrote FLUXNET raw archive audit CSV: {result.output_csv}")
    print(f"Wrote FLUXNET raw archive audit report: {result.output_report}")
    print(f"Status: {result.status}")
    return 0 if result.status == "READY_FOR_ANOMALY_PREPROCESSING" else 2


def fluxnet_anomaly_preprocess(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_fluxnet_anomaly_preprocess_command(
        audit_csv=args.audit,
        output_path=args.output,
        report_path=args.report,
        min_climatology_samples=args.min_climatology_samples,
    )
    if completed_for_input:
        print(f"Wrote FLUXNET anomalies: {args.output}")
        print(f"Wrote FLUXNET anomaly preprocessing report: {report_path}")
    else:
        print(f"Wrote FLUXNET anomaly preprocessing readiness report: {report_path}")
    return 0 if completed_for_input else 2


def predictive_validation_summary(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_predictive_validation_summary_command(
        baseline_path=args.baseline,
        temporal_path=args.temporal,
        spatial_path=args.spatial,
        output_path=args.output,
        report_path=args.report,
    )
    if completed_for_input:
        print(f"Wrote predictive validation summary: {args.output}")
        print(f"Wrote predictive validation report: {report_path}")
    else:
        print(f"Wrote predictive validation readiness report: {report_path}")
    return 0


def uncertainty_audit(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_uncertainty_audit_command(
        baseline_path=args.baseline,
        temporal_path=args.temporal,
        spatial_path=args.spatial,
        output_path=args.output,
        report_path=args.report,
    )
    if completed_for_input:
        print(f"Wrote uncertainty intervals: {args.output}")
        print(f"Wrote uncertainty audit report: {report_path}")
    else:
        print(f"Wrote uncertainty readiness report: {report_path}")
    return 0


def placebo_validation(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_placebo_validation_command(
        input_path=args.input,
        output_path=args.output,
        report_path=args.report,
        top_n=args.top_n,
    )
    if completed_for_input:
        print(f"Wrote placebo validation metrics: {args.output}")
        print(f"Wrote placebo validation report: {report_path}")
    else:
        print(f"Wrote placebo validation readiness report: {report_path}")
    return 0


def threshold_sensitivity(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_threshold_sensitivity_command(
        input_path=args.input,
        output_path=args.output,
        report_path=args.report,
        minimum_duration=args.minimum_duration,
    )
    if completed_for_input:
        print(f"Wrote threshold sensitivity metrics: {args.output}")
        print(f"Wrote threshold sensitivity report: {report_path}")
    else:
        print(f"Wrote threshold sensitivity readiness report: {report_path}")
    return 0


def biome_stratified_validation(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_biome_stratified_validation_command(
        modeling_path=args.modeling,
        biome_col=args.biome_col,
        output_path=args.output,
        report_path=args.report,
        top_n=args.top_n,
    )
    if completed_for_input:
        print(f"Wrote biome-stratified metrics: {args.output}")
        print(f"Wrote biome-stratified validation report: {report_path}")
    else:
        print(f"Wrote biome-stratified validation readiness report: {report_path}")
    return 0


def sensor_cross_validation(args: argparse.Namespace) -> int:
    completed_for_input, report_path = run_sensor_cross_validation_command(
        modis_path=args.modis,
        external_path=args.external,
        output_path=args.output,
        report_path=args.report,
    )
    if completed_for_input:
        print(f"Wrote sensor cross-validation metrics: {args.output}")
        print(f"Wrote sensor cross-validation report: {report_path}")
    else:
        print(f"Wrote sensor cross-validation readiness report: {report_path}")
    return 0


def minimum_evidence_slice(args: argparse.Namespace) -> int:
    slice_report, output, csv_output = run_minimum_evidence_slice_command(
        root=args.root,
        output_path=args.output,
        csv_path=args.csv,
    )
    print(f"Wrote minimum evidence-slice gate report: {output}")
    print(f"Wrote minimum evidence-slice status CSV: {csv_output}")
    print(f"Status: {'READY_FOR_PILOT_REVIEW' if slice_report.ready else 'NOT_READY'}")
    return 0 if slice_report.ready else 2


def generate_pilot_figures(args: argparse.Namespace) -> int:
    result = run_pilot_figure_generation_command(
        event_path=args.events,
        attribution_path=args.attribution,
        lag_response_path=args.lag_response,
        predictive_path=args.predictive,
        output_dir=args.output_dir,
        manifest_path=args.manifest,
        report_path=args.report,
    )
    print(f"Wrote pilot figure report: {result.report_path}")
    print(f"Wrote pilot figure manifest: {result.manifest_path}")
    if result.completed_for_input:
        for path in result.figure_paths:
            print(f"Wrote pilot figure: {path}")
    else:
        print("Status: NOT_READY")
    return 0 if result.completed_for_input else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nature-climate-ai")
    subparsers = parser.add_subparsers(required=True)

    describe = subparsers.add_parser("describe-study")
    describe.add_argument("--config", default="config/study.yaml")
    describe.set_defaults(func=describe_study)

    claims = subparsers.add_parser("check-claims")
    claims.add_argument("--manuscript", default="manuscript/nature_article_draft.md")
    claims.set_defaults(func=check_claims)

    format_audit = subparsers.add_parser("manuscript-format-audit")
    format_audit.add_argument("--manuscript", default="manuscript/nature_article_draft.md")
    format_audit.add_argument("--journal", choices=("nature", "science"), default="nature")
    format_audit.add_argument("--output", default="results/submission/manuscript_format_audit.md")
    format_audit.set_defaults(func=manuscript_format_audit)

    package_audit = subparsers.add_parser("submission-package-audit")
    package_audit.add_argument("--root", default=".")
    package_audit.add_argument("--output", default="manuscript/submission_package_audit.md")
    package_audit.add_argument("--csv", default="manuscript/submission_package_status.csv")
    package_audit.set_defaults(func=submission_package_audit)

    dashboard = subparsers.add_parser("readiness-dashboard")
    dashboard.add_argument("--root", default=".")
    dashboard.add_argument("--manuscript", default="manuscript/nature_article_draft.md")
    dashboard.add_argument("--registry", default="evidence/registry.yaml")
    dashboard.add_argument("--config", default="config/study.yaml")
    dashboard.add_argument("--reference-metadata", default="manuscript/reference_metadata.yaml")
    dashboard.add_argument("--output", default="reproducibility/readiness_dashboard.md")
    dashboard.add_argument("--csv", default="reproducibility/readiness_dashboard.csv")
    dashboard.set_defaults(func=readiness_dashboard)

    figures = subparsers.add_parser("write-figure-plan")
    figures.add_argument("--output", default="figures/generated_figure_plan.md")
    figures.set_defaults(func=write_figure_plan)

    refs = subparsers.add_parser("reference-audit")
    refs.add_argument("--metadata", default="manuscript/reference_metadata.yaml")
    refs.add_argument("--output", default="manuscript/reference_audit.md")
    refs.add_argument("--status-csv", default="manuscript/reference_status.csv")
    refs.set_defaults(func=reference_audit)

    authors = subparsers.add_parser("author-metadata-audit")
    authors.add_argument("--metadata", default="manuscript/author_metadata.yaml")
    authors.add_argument("--output", default="manuscript/author_metadata_audit.md")
    authors.add_argument("--csv", default="manuscript/author_metadata_status.csv")
    authors.set_defaults(func=author_metadata_audit)

    figure_assets = subparsers.add_parser("generate-figure-assets")
    figure_assets.add_argument("--config", default="config/study.yaml")
    figure_assets.add_argument("--output-dir", default="figures/generated")
    figure_assets.add_argument("--manifest", default="figures/generated/figure_manifest.csv")
    figure_assets.add_argument("--report", default="figures/generated/figure_generation_report.md")
    figure_assets.set_defaults(func=generate_figure_assets)

    evidence = subparsers.add_parser("evidence-status")
    evidence.add_argument("--registry", default="evidence/registry.yaml")
    evidence.set_defaults(func=evidence_status)

    artifact_audit = subparsers.add_parser("evidence-artifact-audit")
    artifact_audit.add_argument("--registry", default="evidence/registry.yaml")
    artifact_audit.add_argument("--root", default=".")
    artifact_audit.add_argument("--output", default="evidence/artifact_audit.md")
    artifact_audit.add_argument("--csv", default="evidence/artifact_audit.csv")
    artifact_audit.set_defaults(func=evidence_artifact_audit)

    checksum = subparsers.add_parser("checksum-audit")
    checksum.add_argument("--root", default="data")
    checksum.add_argument("--output", default="data/checksums/data_checksum_audit.md")
    checksum.add_argument("--csv", default="data/checksums/data_checksums.csv")
    checksum.set_defaults(func=checksum_audit)

    placeholders = subparsers.add_parser("placeholder-map")
    placeholders.add_argument("--manuscript", default="manuscript/nature_article_draft.md")
    placeholders.add_argument("--output", default="manuscript/placeholder_evidence_map.md")
    placeholders.add_argument("--csv", default="manuscript/placeholder_evidence_map.csv")
    placeholders.set_defaults(func=placeholder_map)

    reproducibility = subparsers.add_parser("reproducibility-audit")
    reproducibility.add_argument("--output", default="reproducibility/environment_report.md")
    reproducibility.add_argument("--command-manifest", default="reproducibility/command_manifest.csv")
    reproducibility.add_argument("--environment-yml", default="reproducibility/environment.yml")
    reproducibility.add_argument("--requirements-lock", default="reproducibility/requirements-lock.txt")
    reproducibility.add_argument("--seed-manifest", default="reproducibility/random_seed_manifest.yaml")
    reproducibility.add_argument("--compute-budget", default="reproducibility/compute_budget.md")
    reproducibility.set_defaults(func=reproducibility_audit)

    smoke = subparsers.add_parser("pipeline-smoke-test")
    smoke.add_argument("--output-dir", default="outputs/smoke")
    smoke.add_argument("--report", default="reproducibility/pipeline_smoke_report.md")
    smoke.add_argument("--manifest", default="reproducibility/pipeline_smoke_manifest.csv")
    smoke.add_argument("--config", default="config/study.yaml")
    smoke.set_defaults(func=pipeline_smoke_test)

    access = subparsers.add_parser("data-access-plan")
    access.add_argument("--config", default="config/study.yaml")
    access.add_argument("--manifest", default="data/metadata/data_access_manifest.csv")
    access.add_argument("--report", default="data/metadata/data_access_plan.md")
    access.set_defaults(func=data_access_plan)

    access_templates = subparsers.add_parser("data-access-template-audit")
    access_templates.add_argument("--root", default=".")
    access_templates.add_argument("--output", default="data/metadata/data_access_template_audit.md")
    access_templates.add_argument("--csv", default="data/metadata/data_access_template_status.csv")
    access_templates.set_defaults(func=data_access_template_audit)

    provider_requests = subparsers.add_parser("provider-request-templates")
    provider_requests.add_argument("--config", default="config/study.yaml")
    provider_requests.add_argument("--output-dir", default="data/metadata/provider_requests")
    provider_requests.add_argument("--manifest", default="data/metadata/provider_request_manifest.csv")
    provider_requests.add_argument("--report", default="data/metadata/provider_request_templates.md")
    provider_requests.set_defaults(func=provider_request_templates)

    release = subparsers.add_parser("public-release-audit")
    release.add_argument("--root", default=".")
    release.add_argument("--output", default="reproducibility/public_release_audit.md")
    release.add_argument("--csv", default="reproducibility/public_release_status.csv")
    release.set_defaults(func=public_release_audit)

    gate = subparsers.add_parser("submission-gate")
    gate.add_argument("--manuscript", default="manuscript/nature_article_draft.md")
    gate.add_argument("--registry", default="evidence/registry.yaml")
    gate.set_defaults(func=submission_gate)

    qc = subparsers.add_parser("e00-data-qc")
    qc.add_argument("--config", default="config/study.yaml")
    qc.add_argument("--registry", default="evidence/registry.yaml")
    qc.add_argument("--root", default=".")
    qc.add_argument("--output", default="results/qc/e00_data_qc_report.md")
    qc.set_defaults(func=e00_data_qc)

    e01 = subparsers.add_parser("e01-event-catalogue")
    e01.add_argument("--input", default="data/processed/modis_anomalies.csv")
    e01.add_argument("--output-dir", default="results/stress_events")
    e01.add_argument("--date-col", default="date")
    e01.add_argument("--unit-col", default="pixel_id")
    e01.add_argument("--value-col", default="evi_anomaly")
    e01.add_argument("--percentile", type=float, default=10)
    e01.add_argument("--minimum-duration", type=int, default=2)
    e01.set_defaults(func=e01_event_catalogue)

    anomalies = subparsers.add_parser("modis-anomalies")
    anomalies.add_argument("--input", default="data/interim/modis_quality_filtered.csv")
    anomalies.add_argument("--output", default="data/processed/modis_anomalies.csv")
    anomalies.add_argument("--report", default="results/qc/modis_anomaly_qc_report.md")
    anomalies.add_argument("--min-climatology-samples", type=int, default=2)
    anomalies.set_defaults(func=modis_anomalies)

    quality = subparsers.add_parser("modis-quality-filter")
    quality.add_argument("--input", default="data/raw/modis_observations.csv")
    quality.add_argument("--output", default="data/interim/modis_quality_filtered.csv")
    quality.add_argument("--report", default="results/qc/modis_quality_filter_report.md")
    quality.add_argument("--max-vi-usefulness", type=int, default=11)
    quality.set_defaults(func=modis_quality_filter)

    modis_raw = subparsers.add_parser("modis-raw-inventory")
    modis_raw.add_argument("--input-dir", default="data/raw/modis")
    modis_raw.add_argument("--output", default="data/metadata/modis_raw_inventory.csv")
    modis_raw.add_argument("--report", default="data/metadata/modis_raw_inventory.md")
    modis_raw.add_argument("--start-year", type=int, default=2001)
    modis_raw.add_argument("--end-year", type=int, default=2025)
    modis_raw.set_defaults(func=modis_raw_inventory)

    raw_era5 = subparsers.add_parser("era5-raw-aggregate")
    raw_era5.add_argument("--input-dir", default="data/raw/era5/cds_8c5868ad2f6b9db27f57ebaaeb460755")
    raw_era5.add_argument("--output", default="data/interim/era5_composite_climate.csv")
    raw_era5.add_argument("--report", default="results/qc/era5_raw_aggregate_report.md")
    raw_era5.add_argument("--config", default="config/study.yaml")
    raw_era5.add_argument("--spatial-stride", type=int, default=1)
    raw_era5.set_defaults(func=era5_raw_aggregate)

    climate = subparsers.add_parser("era5-climate-features")
    climate.add_argument("--input", default="data/interim/era5_composite_climate.csv")
    climate.add_argument("--output", default="data/processed/climate_lag_features.csv")
    climate.add_argument("--report", default="results/qc/era5_climate_feature_report.md")
    climate.add_argument("--config", default="config/study.yaml")
    climate.add_argument("--min-climatology-samples", type=int, default=2)
    climate.add_argument("--variables", default=None, help="Comma-separated ERA5 variables for explicit pilot runs")
    climate.set_defaults(func=era5_climate_features)

    model_data = subparsers.add_parser("modeling-dataset")
    model_data.add_argument("--climate", default="data/processed/climate_lag_features.csv")
    model_data.add_argument("--events", default="results/stress_events/event_catalogue_summary.csv")
    model_data.add_argument("--anomalies", default="data/processed/modis_anomalies.csv")
    model_data.add_argument("--output", default="data/processed/modeling_dataset.csv")
    model_data.add_argument("--report", default="results/qc/modeling_dataset_report.md")
    model_data.set_defaults(func=modeling_dataset)

    baselines = subparsers.add_parser("baseline-evaluation")
    baselines.add_argument("--input", default="data/processed/modeling_dataset.csv")
    baselines.add_argument("--output", default="results/validation/baseline_metrics.csv")
    baselines.add_argument("--report", default="results/validation/baseline_comparison.md")
    baselines.add_argument("--config", default="config/study.yaml")
    baselines.set_defaults(func=baseline_evaluation)

    precursor = subparsers.add_parser("precursor-discovery")
    precursor.add_argument("--input", default="data/processed/modeling_dataset.csv")
    precursor.add_argument("--attribution", default="results/modeling/feature_attribution_table.csv")
    precursor.add_argument("--lag-response", default="results/modeling/lag_response_summary.csv")
    precursor.add_argument("--report", default="results/modeling/precursor_discovery_report.md")
    precursor.set_defaults(func=precursor_discovery)

    temporal = subparsers.add_parser("temporal-holdout-validation")
    temporal.add_argument("--modeling", default="data/processed/modeling_dataset.csv")
    temporal.add_argument("--candidates", default="results/modeling/feature_attribution_table.csv")
    temporal.add_argument("--output", default="results/validation/temporal_holdout_metrics.csv")
    temporal.add_argument("--report", default="results/validation/temporal_holdout_report.md")
    temporal.add_argument("--config", default="config/study.yaml")
    temporal.add_argument("--top-n", type=int, default=10)
    temporal.set_defaults(func=temporal_holdout_validation)

    spatial = subparsers.add_parser("spatial-holdout-validation")
    spatial.add_argument("--modeling", default="data/processed/modeling_dataset.csv")
    spatial.add_argument("--candidates", default="results/modeling/feature_attribution_table.csv")
    spatial.add_argument("--output", default="results/validation/spatial_holdout_metrics.csv")
    spatial.add_argument("--report", default="results/validation/spatial_holdout_report.md")
    spatial.add_argument("--region-col", default="region")
    spatial.add_argument("--top-n", type=int, default=10)
    spatial.set_defaults(func=spatial_holdout_validation)

    fluxnet = subparsers.add_parser("fluxnet-validation")
    fluxnet.add_argument("--fluxnet", default="data/processed/fluxnet_anomalies.csv")
    fluxnet.add_argument("--windows", default="results/fluxnet/predicted_stress_windows.csv")
    fluxnet.add_argument("--output", default="results/fluxnet/site_anomaly_metrics.csv")
    fluxnet.add_argument("--report", default="results/fluxnet/validation_summary.md")
    fluxnet.set_defaults(func=fluxnet_validation)

    fluxnet_raw = subparsers.add_parser("fluxnet-raw-audit")
    fluxnet_raw.add_argument("--input-dir", default="data/raw/fluxnet")
    fluxnet_raw.add_argument("--output", default="data/metadata/fluxnet_raw_archive_audit.csv")
    fluxnet_raw.add_argument("--report", default="data/metadata/fluxnet_raw_archive_audit.md")
    fluxnet_raw.set_defaults(func=fluxnet_raw_audit)

    fluxnet_anomalies = subparsers.add_parser("fluxnet-anomalies")
    fluxnet_anomalies.add_argument("--audit", default="data/metadata/fluxnet_raw_archive_audit.csv")
    fluxnet_anomalies.add_argument("--output", default="data/processed/fluxnet_anomalies.csv")
    fluxnet_anomalies.add_argument("--report", default="results/fluxnet/fluxnet_anomaly_preprocess_report.md")
    fluxnet_anomalies.add_argument("--min-climatology-samples", type=int, default=2)
    fluxnet_anomalies.set_defaults(func=fluxnet_anomaly_preprocess)

    predictive = subparsers.add_parser("predictive-validation-summary")
    predictive.add_argument("--baseline", default="results/validation/baseline_metrics.csv")
    predictive.add_argument("--temporal", default="results/validation/temporal_holdout_metrics.csv")
    predictive.add_argument("--spatial", default="results/validation/spatial_holdout_metrics.csv")
    predictive.add_argument("--output", default="results/validation/predictive_validation_summary.csv")
    predictive.add_argument("--report", default="results/validation/predictive_validation_summary.md")
    predictive.set_defaults(func=predictive_validation_summary)

    uncertainty = subparsers.add_parser("uncertainty-audit")
    uncertainty.add_argument("--baseline", default="results/validation/baseline_metrics.csv")
    uncertainty.add_argument("--temporal", default="results/validation/temporal_holdout_metrics.csv")
    uncertainty.add_argument("--spatial", default="results/validation/spatial_holdout_metrics.csv")
    uncertainty.add_argument("--output", default="results/validation/uncertainty_intervals.csv")
    uncertainty.add_argument("--report", default="results/validation/uncertainty_audit.md")
    uncertainty.set_defaults(func=uncertainty_audit)

    placebo = subparsers.add_parser("placebo-validation")
    placebo.add_argument("--input", default="data/processed/modeling_dataset.csv")
    placebo.add_argument("--output", default="results/validation/placebo_metrics.csv")
    placebo.add_argument("--report", default="results/validation/placebo_validation.md")
    placebo.add_argument("--top-n", type=int, default=10)
    placebo.set_defaults(func=placebo_validation)

    threshold = subparsers.add_parser("threshold-sensitivity")
    threshold.add_argument("--input", default="data/processed/modis_anomalies.csv")
    threshold.add_argument("--output", default="results/validation/threshold_sensitivity.csv")
    threshold.add_argument("--report", default="results/validation/threshold_sensitivity.md")
    threshold.add_argument("--minimum-duration", type=int, default=2)
    threshold.set_defaults(func=threshold_sensitivity)

    biome = subparsers.add_parser("biome-stratified-validation")
    biome.add_argument("--modeling", default="data/processed/modeling_dataset.csv")
    biome.add_argument("--biome-col", default="biome")
    biome.add_argument("--output", default="results/validation/biome_metrics.csv")
    biome.add_argument("--report", default="results/validation/biome_validation.md")
    biome.add_argument("--top-n", type=int, default=10)
    biome.set_defaults(func=biome_stratified_validation)

    sensor = subparsers.add_parser("sensor-cross-validation")
    sensor.add_argument("--modis", default="data/processed/modis_anomalies.csv")
    sensor.add_argument("--external", default="data/processed/external_vegetation_anomalies.csv")
    sensor.add_argument("--output", default="results/validation/sensor_cross_validation.csv")
    sensor.add_argument("--report", default="results/validation/sensor_cross_validation.md")
    sensor.set_defaults(func=sensor_cross_validation)

    pilot = subparsers.add_parser("minimum-evidence-slice")
    pilot.add_argument("--root", default=".")
    pilot.add_argument("--output", default="results/pilot/minimum_evidence_slice_report.md")
    pilot.add_argument("--csv", default="results/pilot/minimum_evidence_slice_status.csv")
    pilot.set_defaults(func=minimum_evidence_slice)

    pilot_figures = subparsers.add_parser("generate-pilot-figures")
    pilot_figures.add_argument("--events", default="results/stress_events/event_catalogue_summary.csv")
    pilot_figures.add_argument("--attribution", default="results/modeling/feature_attribution_table.csv")
    pilot_figures.add_argument("--lag-response", default="results/modeling/lag_response_summary.csv")
    pilot_figures.add_argument("--predictive", default="results/validation/predictive_validation_summary.csv")
    pilot_figures.add_argument("--output-dir", default="figures/generated")
    pilot_figures.add_argument("--manifest", default="figures/generated/pilot_figure_manifest.csv")
    pilot_figures.add_argument("--report", default="figures/generated/pilot_figure_generation_report.md")
    pilot_figures.set_defaults(func=generate_pilot_figures)

    era5 = subparsers.add_parser("download-era5")
    era5.add_argument("--config", default="config/study.yaml")
    era5.add_argument("--output-dir", default="data/raw/era5")
    era5.add_argument("--log", default="data/metadata/era5_download_log.csv")
    era5.add_argument("--year-start", type=int, default=None)
    era5.add_argument("--year-end", type=int, default=None)
    era5.add_argument("--months", default=None, help="Comma-separated months e.g. 1,6,12")
    era5.add_argument("--only", choices=("single", "land", "both"), default="both")
    era5.add_argument("--dry-run", action="store_true")
    era5.set_defaults(func=era5_download)

    status = subparsers.add_parser("download-status")
    status.add_argument("--log", default="data/metadata/era5_download_log.csv")
    status.add_argument("--output", default="data/metadata/era5_download_status.md")
    status.set_defaults(func=download_status)

    modis = subparsers.add_parser("download-modis")
    modis.add_argument("--config", default="config/study.yaml")
    modis.add_argument("--output-dir", default="data/raw/modis")
    modis.add_argument("--log", default="data/metadata/modis_download_log.csv")
    modis.add_argument("--year-start", type=int, default=None)
    modis.add_argument("--year-end", type=int, default=None)
    modis.add_argument("--tiles", default=None)
    modis.add_argument("--dry-run", action="store_true")
    modis.set_defaults(func=modis_download)

    fluxnet_help = subparsers.add_parser("fluxnet-instructions")
    fluxnet_help.set_defaults(func=fluxnet_instructions)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
