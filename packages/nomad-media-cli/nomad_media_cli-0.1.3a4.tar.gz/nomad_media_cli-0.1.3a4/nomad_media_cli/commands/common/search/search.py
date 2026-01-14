import click
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option('--query', default=None, help='Search query')
@click.option('--offset', default=0, help='Page offset')
@click.option('--size', default=100, help='Page size')
@click.option('--filters', default=None, help='Filters')
@click.option('--sort-fields', default=None, help='Sort fields')
@click.option('--search-result-fields', default=None, help='Search result fields')
@click.option('--full-url-field-names', default=None, help='Full URL field names')
@click.option('--distinct-on-field-name', default=None, help='Distinct on field name')
@click.option('--include-video-clips', is_flag=True, help='Include video clips')
@click.option('--similar-asset-id', default=None, help='Similar asset ID')
@click.option('--min-score', default=None, help='Minimum score')
@click.option('--exclude-total-record-count', is_flag=True, help='Exclude total record count')
@click.option('--filter-binder', default=None, help='Filter binder')
@click.option('--use-llm-search', is_flag=True, help='Use LLM search')
@click.option('--include-internal-fields-in-results', is_flag=True, help='Include internal fields in results')
def search(query, offset, size, filters, sort_fields, search_result_fields, full_url_field_names, distinct_on_field_name, include_video_clips, similar_asset_id, min_score, exclude_total_record_count, filter_binder, use_llm_search, include_internal_fields_in_results):
    """CLI for search function."""
    initialize_sdk()
    nomad_sdk = click.get_current_context().obj["nomad_sdk"]
    
    result = nomad_sdk.search(
        query=query,
        offset=offset,
        size=size,
        filters=filters,
        sort_fields=sort_fields,
        search_result_fields=search_result_fields,
        full_url_field_names=full_url_field_names,
        distinct_on_field_name=distinct_on_field_name,
        include_video_clips=include_video_clips,
        similar_asset_id=similar_asset_id,
        min_score=min_score,
        exclude_total_record_count=exclude_total_record_count,
        filter_binder=filter_binder,
        use_llm_search=use_llm_search,
        include_internal_fields_in_results=include_internal_fields_in_results
    )
    click.echo(result)