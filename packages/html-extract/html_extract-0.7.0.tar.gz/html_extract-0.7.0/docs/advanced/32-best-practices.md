# Best Practices

Recommended practices for using HTML Extract effectively.

## Configuration

1. **Organize Data Consistently**: Follow the standard directory structure for easy processing

2. **Use Config Templates**: Start with a template and customize it rather than creating from scratch

3. **Test on Single Files First**: Before processing large batches, test your config on a single file

4. **Mark Required Attributes**: Use `required: true` for critical columns (like `link` and `title`) to ensure data quality

5. **Use Fallback Selectors**: Add `fallback_selector` to handle minor HTML structure changes

6. **Include Metadata Attributes**: Add `source_file`, `scrape_date`, and `source_path` to track data provenance

## Data Quality

1. **Validate Output**: Always check a few rows of output to ensure extraction is working correctly

2. **Test Incrementally**: Start with a simple config and add complexity gradually

3. **Use Browser Dev Tools**: Inspect HTML structure to find correct selectors

4. **Handle Missing Data**: Use `required: false` for optional attributes that may not always be present

## Processing

1. **Process in Batches**: For large datasets, use `batch_extract()` with `max_workers` parameter for multiprocessing

2. **Use Streaming**: For very large batches, use streaming to file to reduce memory usage

3. **Reuse Config Objects**: Load config once and reuse for multiple files

4. **Error Handling**: Implement proper error handling in production code

## Organization

1. **Version Control Configs**: Track changes to config files to understand data evolution

2. **Document Custom Attributes**: Add comments in YAML to explain non-obvious extraction logic

3. **Keep Configs Separate**: Maintain separate configs for different categories or use cases

4. **Test Before Production**: Always test configs on sample data before processing full datasets

## Performance

1. **Use Appropriate Workers**: Set `max_workers` based on your system capabilities

2. **Choose Right Processing Mode**: Use multiprocessing for CPU-bound tasks, threading for I/O-bound

3. **Stream Large Batches**: Use streaming mode for memory-efficient processing

4. **Process Incrementally**: For very large datasets, process in smaller batches

## See Also

- [Performance Optimization](30-performance.md) - Performance tips
- [Custom Processing](31-custom-processing.md) - Advanced processing techniques
- [Configuration Reference](../shared/20-configuration-reference.md) - Complete config guide
