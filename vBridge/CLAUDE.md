# Vertical bridge project memory

## Development Practices

- when comparing output to excel documents, always use the /utils directory

- Use existing code systems and tools before creating new ones. Check src/ modular structure: src/core/ for calculators, src/data/ for validators and processors, src/output/ for output managers, and src/config/ for utilities and settings.

- Always read files before editing them. Never write new files unless explicitly required.

- Documentation principle: Always integrate new insights, patterns, and lessons into existing documentation (faq.md, troubleshooting.md, methodology docs) rather than creating new files. This keeps documentation organized and maintainable.

- Mix Bridge contribution calculations must run in specific sequence: Traditional Mix Bridge for absolute metrics first, then MixRate Bridge for rate metrics, then sum_contributions_to_total last to aggregate campaign contributions into total row. Never mark complete until totals are summed.

- Rate metrics use different methodologies: ACoS uses MixRate Bridge with Infinity Error via ROAS inverse to prevent division by zero. ROAS Conversion Rate CTR CPC use Standard MixRate Bridge with appropriate mix determinants: ROAS uses Spend, CTR uses Impressions, Conversion Rate and CPC use Clicks.

- Mathematical consistency requirement: campaign contributions must sum exactly to total contributions. Use tolerance of 0.01 for validation. All rate metrics should have non-zero contributions when properly implemented.

- Missing percentage change calculation for rate metrics is common bug. Always implement percentage change for all metrics not just absolute metrics.

- Metric categorization: absolute metrics like Spend Total Ad Sales Impressions use Traditional Mix Bridge. ACoS uses MixRate Bridge with infinity error handling. ROAS Conversion Rate CTR CPC use Standard MixRate Bridge.

- Output system: use output/current/LATEST_mixbridge.csv for latest results. Auto-archive old files. Timestamped files go in output/analyses/ for history. Rich metadata in output/current/LATEST_mixbridge_info.json.

- When implementing multiple methodologies, check column existence correctly: use metric name - January 2025 not just metric name when checking if columns exist in dataframe.

- Validate implementation by checking that all KPIs have P1 P2 net change percentage change and contribution values with proper mathematical consistency across all methodologies.

- when creating ad hoc scripts for testing, analysis, debugging, or verification store the new file in relevant scripts folder

- Use /utils for Excel comparisons and production validation, /scripts for debugging and ad-hoc analysis (see docs/scripts-vs-utils-guide.md)

- MixBridge v2 uses clean modular architecture: import from src.core.* src.data.* src.output.* src.config.* src.common.* or use package-level imports like "from src import BridgeCalculator, MetricDefinitions" for convenience
