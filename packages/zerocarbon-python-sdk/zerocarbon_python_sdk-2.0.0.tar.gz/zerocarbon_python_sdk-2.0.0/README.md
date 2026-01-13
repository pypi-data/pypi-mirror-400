# ZeroCarbon Python SDK

Official Python client for [ZeroCarbon.codes](https://zerocarbon.codes) - India's leading Carbon Accounting & Offsetting API.

## Installation

```bash
pip install zerocarbon-sdk
```

## Quick Start

```python
from zerocarbon import ZeroCarbon

# Initialize client
client = ZeroCarbon(api_key="YOUR_API_KEY")

# Calculate flight emissions
emissions = client.calculate.flight(
    origin="DEL",
    destination="BOM",
    cabin_class="economy"
)
print(f"Emissions: {emissions['emissions_kg_co2e']} kg CO2e")

# Get offset recommendations
offsets = client.offsets.get_recommendations(
    emissions_kg_co2e=emissions['emissions_kg_co2e'],
    preferred_region="India"
)
print(f"Top project: {offsets['recommendations'][0]['name']}")

# Purchase and retire credits
transaction = client.offsets.purchase(
    project_id=offsets['recommendations'][0]['project_id'],
    quantity_kg_co2e=emissions['emissions_kg_co2e'],
    retirement_reason="Business flight offsetting"
)
print(f"Certificate: {transaction['certificate_url']}")
```

## Features

- ✅ Calculate emissions from flights, electricity, fuel, and more
- ✅ AI-powered spend-based emission matching
- ✅ Carbon offset recommendations
- ✅ Purchase and retire carbon credits
- ✅ Generate BRSR-compliant reports
- ✅ Webhook support
- ✅ Test mode for development

## Documentation

Full documentation: https://docs.zerocarbon.codes

## Examples

### Calculate Electricity Emissions

```python
emissions = client.calculate.electricity(
    amount_kwh=1000,
    country="IN",
    state="Maharashtra"
)
# Returns: 820 kg CO2e (using India grid factor)
```

### Smart Spend Matching

```python
emissions = client.calculate.spend(
    amount=100000,
    currency="INR",
    category="electricity",
    description="Monthly office electricity bill"
)
# AI automatically matches to emission factors
```

### Generate BRSR Report

```python
report = client.brsr.generate_report(
    company_id="comp_123",
    financial_year="2024-25",
    format="pdf"
)
print(report['download_url'])
```

## Test Mode

Enable test mode to avoid real charges:

```python
client = ZeroCarbon(
    api_key="test_YOUR_API_KEY",
    test_mode=True
)
```

## License

MIT License - see LICENSE file for details.

## Support

- Email: support@zerocarbon.codes
- Docs: https://docs.zerocarbon.codes
- GitHub: https://github.com/zerocarbon/python-sdk
